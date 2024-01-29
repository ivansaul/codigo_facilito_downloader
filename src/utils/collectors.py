"""Collectors for Facilito API"""

from playwright.sync_api import Page

from src.errors import VideoError
from src.models.course import Course, CourseSection
from src.models.video import MediaType, Video
from src.utils import expanders
from src.utils.logger import logger


def get_video_detail_sync(url: str, page: Page) -> Video:
    """Retrieve detailed information for a video from its URL.

    Args:
        url (str): The URL of the video page.
        page (Page): The Playwright page object.

    Returns:
        Video: An instance of the Video model with the retrieved details.
    """

    page.goto(url=url, wait_until=None)

    # search video title
    title = page.locator(
        "h1[class='ibm bold-600 no-margin f-text-22'], h1[class='ibm bold-600 no-margin f-text-48']"
    ).inner_text()

    video_id = page.locator("input[name='video_id']").first.get_attribute("value")
    course_id = page.locator("input[name='course_id']").get_attribute("value")

    if video_id is None or course_id is None:
        raise VideoError("Video ID or Course ID not found")

    # get video m3u8 url
    base_m3u8_url = "https://video-storage.codigofacilito.com"
    m3u8_url = f"{base_m3u8_url}/hls/{course_id}/{video_id}/playlist.m3u8"

    # check media type
    media_type: MediaType = None

    if "/videos/" in url:
        media_type = "streaming"
    if "/articulos/" in url:
        media_type = "reading"
    if media_type is None:
        raise VideoError("Media type not found")

    return Video(
        id=video_id,
        url=url,
        m3u8_url=m3u8_url,
        title=title,
        media_type=media_type,
    )


def get_course_detail_sync(url: str, page: Page) -> Course:
    """
    Retrieves detailed information about a course from a given URL.

    Args:
        url (str): The URL of the course to be detailed.
        page (Page): The playwright page object to interact with the webpage.

    Returns:
        Course: An object containing the course details."""

    page.goto(url=url, wait_until=None)

    # expand collapsed sections
    expanders.expand_course_sections(page)

    # get course title
    title = page.title()

    # get course sections
    sections = _get_sections(page)

    course = Course(
        url=url,
        title=title,
        sections=sections,
    )

    return course


def _get_sections(page: Page) -> list[CourseSection]:
    """Get course sections from a page.

    This function collects all course sections from the given page by looking for
    specific HTML div elements with class 'f-top-16' and extracts their corresponding titles.

    Args:
        page (Page): The playwright page object representing the web page.

    Returns:
        list[CourseSection]: A list of CourseSection objects.
    """
    sections: list[CourseSection] = []

    # possibly some containers are empty
    sections_container_divs = page.query_selector_all("div[class='f-top-16']")

    for div in sections_container_divs:
        title_match = div.query_selector("h4")
        if title_match is None:
            continue

        logger.debug("[Section Title] %s", title_match.inner_text())

        # subtitle_match = div.query_selector("span[class='bold f-grey-tex']")
        # if subtitle_match is not None:
        #     logger.debug("[Section Subtitle] %s", subtitle_match.inner_text())

        a_tags = div.query_selector_all("a")
        href_values = [a.get_attribute("href") for a in a_tags]
        all_video_urls = [f"https://codigofacilito.com{href}" for href in href_values]

        logger.debug("This section has %s videos", len(all_video_urls))

        sections.append(
            CourseSection(
                title=title_match.inner_text(),
                videos_url=all_video_urls,
            ),
        )

    return sections


__all__ = [
    "get_video_detail_sync",
    "get_course_detail_sync",
]
