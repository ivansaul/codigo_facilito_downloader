"""Collectors for Facilito API"""

from playwright.sync_api import Page

from src.errors import FacilitoMediaTypeError, FacilitoVideoNotAvailableError
from src.models.course import Course, CourseSection
from src.models.video import MediaType, Video
from src.utils import expanders


def get_video_detail_sync(url: str, page: Page) -> Video:
    """Get video detail from Codigo Facilito"""

    page.goto(url=url, wait_until=None)

    # get video title
    title = page.locator(
        "h1[class='ibm bold-600 no-margin f-text-22'], h1[class='ibm bold-600 no-margin f-text-48']"
    ).inner_text()

    # get video id and course id
    video_id = page.locator("input[name='video_id']").first.get_attribute("value")
    course_id = page.locator("input[name='course_id']").get_attribute("value")

    if video_id is None or course_id is None:
        raise FacilitoVideoNotAvailableError("Video ID or Course ID not found")

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
        raise FacilitoMediaTypeError("Media type not found")

    return Video(
        id=video_id,
        url=url,
        m3u8_url=m3u8_url,
        title=title,
        media_type=media_type,
    )


def get_course_detail_sync(url: str, page: Page) -> Course:
    """Get course detail from Codigo Facilito"""

    page.goto(url=url, wait_until=None)

    # expand collapsed modules
    expanders.expand_course_sections(page)

    # get course title
    title = page.title()

    # get course modules
    sections = _get_modules(page)

    course = Course(
        url=url,
        title=title,
        sections=sections,
    )

    return course


def _get_modules(page: Page) -> list[CourseSection]:
    """Get modules from Codigo Facilito"""
    # //div[@class="f-top-16"] == div[class='f-top-16'] == div.f-top-16
    sections_container_divs = page.query_selector_all("div[class='f-top-16']")

    sections: list[CourseSection] = []
    print("Sections Container divs found: ", len(sections_container_divs))

    for div in sections_container_divs:
        title_match = div.query_selector("h4")
        if title_match is None:
            continue

        print(title_match.inner_text())

        subtitle_match = div.query_selector("span[class='bold f-grey-tex']")
        if subtitle_match is not None:
            print(subtitle_match.inner_text())

        a_tags = div.query_selector_all("a")
        href_values = [a.get_attribute("href") for a in a_tags]
        videos_url = [f"https://codigofacilito.com{href}" for href in href_values]

        print(len(videos_url))
        print("--" * 10)

        sections.append(
            CourseSection(
                title=title_match.inner_text(),
                videos_url=videos_url,
            ),
        )

    return sections


__all__ = [
    "get_video_detail_sync",
    "get_course_detail_sync",
]
