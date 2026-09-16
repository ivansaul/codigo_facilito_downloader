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


async def _wait_for_playlist(playlist_found: asyncio.Event, timeout: float) -> None:
    try:
        await asyncio.wait_for(playlist_found.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass


async def _trigger_player(page) -> None:
    """Start playback so players that lazy-load the manifest request it."""
    try:
        await page.evaluate(
            """() => {
                const video = document.querySelector('video');
                if (!video) return;
                video.muted = true;
                const result = video.play();
                if (result && typeof result.catch === 'function') {
                    result.catch(() => {});
                }
            }"""
        )
    except Exception:
        pass

    for selector in (
        "button.vjs-big-play-button",
        "button.play-icon",
        "button[aria-label*='play' i]",
        "button[title*='play' i]",
    ):
        try:
            locator = page.locator(selector).first
            if await locator.count():
                await locator.click(timeout=1000)
                return
        except Exception:
            continue


async def _player_source(page) -> str | None:
    try:
        return await page.evaluate(
            """() => {
                const video = document.querySelector('video');
                if (video && (video.currentSrc || video.src)) {
                    return video.currentSrc || video.src;
                }
                const source = document.querySelector(
                    'video source, source[type="application/vnd.apple.mpegurl"]'
                );
                return source ? source.src : null;
            }"""
        )
    except Exception:
        return None


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

        timeout = PLAYLIST_TIMEOUT / 1000

        if not playlist_urls:
            await _wait_for_playlist(playlist_found, timeout)

        if not playlist_urls:
            # Some players only request the manifest once playback starts.
            await _trigger_player(page)
            await _wait_for_playlist(playlist_found, timeout)

        player_source = await _player_source(page)

        if playlist_urls:
            url = playlist_urls[0]
            logger.info(f"Playlist URL captured from network: {redact_url(url)}")

        elif player_source and ".m3u8" in player_source:
            url = player_source
            logger.info(f"Playlist URL read from player: {redact_url(url)}")

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
