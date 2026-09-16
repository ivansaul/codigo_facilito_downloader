import asyncio
import re

from playwright.async_api import BrowserContext

from ..constants import VIDEO_BASE_URL, VIDEO_M3U8_URL
from ..errors import AbortError, VideoError
from ..logger import logger
from ..models import Video
from ..ratelimit import (
    RateLimitSettings,
    ThrottleStats,
    redact_url,
    throttled_goto,
)
from ..utils import is_video

M3U8_PATTERN = r"\/hls\/.*?\.m3u8"
PLAYLIST_TIMEOUT = 10 * 1000


async def fetch_video(
    context: BrowserContext,
    url: str,
    settings: RateLimitSettings | None = None,
    stats: ThrottleStats | None = None,
) -> Video:
    VIDEO_ID_SELECTOR = "input[name='video_id']"
    COURSE_ID_SELECTOR = "input[name='course_id']"

    if not is_video(url):
        raise VideoError()

    try:
        page = await context.new_page()

        # The player requests the playlist (possibly a signed url) while loading,
        # so listen before navigating to avoid missing an early request.
        playlist_urls: list[str] = []
        playlist_found = asyncio.Event()

        def on_request(request):
            if ".m3u8" in request.url:
                playlist_urls.append(request.url)
                playlist_found.set()

        page.on("request", on_request)

        await throttled_goto(
            page,
            url,
            settings or RateLimitSettings(),
            stats=stats or ThrottleStats(),
        )

        if not playlist_urls:
            try:
                await asyncio.wait_for(
                    playlist_found.wait(), timeout=PLAYLIST_TIMEOUT / 1000
                )
            except asyncio.TimeoutError:
                pass

        if playlist_urls:
            url = playlist_urls[0]
            logger.info(f"Playlist URL captured from network: {redact_url(url)}")

        elif m3u8_urls := re.findall(M3U8_PATTERN, await page.content()):
            url = VIDEO_BASE_URL + m3u8_urls[0]
            logger.info(f"Playlist URL found in page source: {redact_url(url)}")

        else:
            course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute(
                "value"
            )
            video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute(
                "value"
            )

            if not video_id or not course_id:
                raise VideoError()

            url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)
            logger.warning(
                "Falling back to the static playlist URL, which may be "
                f"unavailable: {redact_url(url)}"
            )

    except AbortError:
        raise
    except Exception:
        raise VideoError()

    finally:
        await page.close()

    return Video(url=url)
