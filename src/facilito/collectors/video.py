from playwright.async_api import BrowserContext

from ..constants import VIDEO_M3U8_URL
from ..errors import VideoError
from ..models import Video
from ..utils import is_video


async def fetch_video(context: BrowserContext, url: str) -> Video:
    VIDEO_ID_SELECTOR = "input[name='video_id']"
    COURSE_ID_SELECTOR = "input[name='course_id']"

    if not is_video(url):
        raise VideoError()

    try:
        page = await context.new_page()
        await page.goto(url)

        course_id = await page.locator(COURSE_ID_SELECTOR).first.get_attribute("value")
        video_id = await page.locator(VIDEO_ID_SELECTOR).first.get_attribute("value")

        if not video_id or not course_id:
            raise VideoError()

        url = VIDEO_M3U8_URL.format(course_id=course_id, video_id=video_id)

    except Exception:
        raise VideoError()

    finally:
        await page.close()

    return Video(url=url)
