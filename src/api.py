"""Synchronous Api to scrape data from Codigo Facilito."""

from playwright.sync_api import sync_playwright

from src.errors import ClientError
from src.models.course import Course
from src.models.video import Video
from src.utils import collectors


class FacilitoApi:
    """Synchronous Api to scrape data from Codigo Facilito."""

    def __init__(
        self,
        headless: bool = False,
        navigation_timeout: int = 30 * 1000,
        navigation_retries: int = 5,
    ):
        self.headless = headless
        self.navigation_timeout = navigation_timeout
        self.navigation_retries = navigation_retries

    def __enter__(self):
        # pylint: disable=attribute-defined-outside-init
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.firefox.launch(headless=self.headless)
        self._context = self._browser.new_context()
        self._context.set_default_navigation_timeout(self.navigation_timeout)
        self._page = self._context.new_page()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._context.close()
        self._browser.close()
        self._playwright.stop()

    @property
    def playwright(self):
        """The playwright instance used for data scraping."""
        if not hasattr(self, "_playwright"):
            raise ClientError("FacilitoApi must be used as a context manager.")
        return self._playwright

    @property
    def browser(self):
        """The browser instance used for data scraping."""
        if not hasattr(self, "_browser"):
            raise ClientError("FacilitoApi must be used as a context manager.")
        return self._browser

    @property
    def context(self):
        """The context instance used for data scraping."""
        if not hasattr(self, "_context"):
            raise ClientError("FacilitoApi must be used as a context manager.")
        return self._context

    def video(self, url: str) -> Video:
        """Get video"""
        page = self._page
        video = collectors.get_video_detail_sync(url, page)
        return video

    def course(self, url: str) -> Course:
        """Get course"""
        page = self._page
        course = collectors.get_course_detail_sync(url, page)
        return course
