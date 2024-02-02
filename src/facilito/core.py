"""
Synchronous Client to scrape data from Codigo Facilito.
"""

from typing import Optional

from playwright.sync_api import sync_playwright

from . import consts, helpers
from .consts import FileType
from .errors import ClientError
from .models.account import Account
from .models.course import Course
from .models.video import Video
from .utils import collectors


class Client:
    """
    Represents a client capable of handling requests
    with Codigo Facilito.
    """

    def __init__(
        self,
        account: Optional[Account] = None,
        headless: bool = False,
        navigation_timeout: int = 30 * 1000,
        navigation_retries: int = 5,
    ):
        self.account = account
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

    @property
    def page(self):
        """The page instance used for data scraping."""
        if not hasattr(self, "_page"):
            raise ClientError("FacilitoApi must be used as a context manager.")
        return self._page

    def video(self, url: str) -> Video:
        """
        Fetch a Codigo Facilito video by its URL.

        Args:
            url (str): The URL of the video to fetch.
        Returns:
            Video: An instance of Video class containing the details of the fetched video.
        Raises:
            URLError: If the URL provided is invalid.
        """
        page = self.page
        video = collectors.get_video_detail_sync(url, page)
        return video

    def course(self, url: str) -> Course:
        """Get course"""
        page = self.page
        course = collectors.get_course_detail_sync(url, page)
        return course

    def take_screenshot(self, url: str, path: str = "screenshot.png"):
        """Take screenshot page"""
        page = self.page
        page.goto(url)
        page.screenshot(path=path)

    def save_as(self, url: str, path: str, file_type: FileType):
        """Save page as pdf or html"""
        # TODO: implement

    def login(self):
        """Login"""
        # TODO: implement

    def refresh_cookies(self) -> None:
        """Refresh cookies from current context"""
        page = self.page
        cookies = page.context.cookies(consts.BASE_URL)
        helpers.save_cookies_to_file(cookies, consts.COOKIES_FILE)
