import os
from pathlib import Path

from playwright.async_api import BrowserContext, Page, async_playwright
from playwright_stealth import Stealth

from . import collectors
from .constants import (
    BASE_URL,
    BROWSER_CHANNELS,
    BROWSER_ENV_VAR,
    LOGIN_URL,
    OFFSCREEN_ARGS,
    SESSION_FILE,
    WINDOW_ENV_VAR,
)
from .errors import AbortError, LoginError
from .helpers import read_json
from .logger import logger
from .ratelimit import RateLimitSettings, ThrottleStats
from .utils import (
    close_pages,
    load_state,
    login_required,
    normalize_cookies,
    save_state,
    try_except_request,
)


class AsyncFacilito:
    def __init__(
        self,
        headless=False,
        browser: str | None = None,
        window: str | None = None,
    ):
        self.browser = browser or os.environ.get(BROWSER_ENV_VAR) or "auto"
        self.window = window or os.environ.get(WINDOW_ENV_VAR) or "offscreen"
        self.headless = headless or self.window == "headless"
        self.authenticated = False

    async def _launch_browser(self):
        """
        Launch a browser with proprietary media codecs when possible.

        The bundled Chromium lacks H.264/AAC, which breaks video playback and
        can stop the player from requesting the HLS playlist. Prefer an
        installed Chrome/Edge channel and fall back to bundled Chromium.
        """
        args = list(OFFSCREEN_ARGS) if self.window == "offscreen" else []

        if self.browser == "chromium":
            return await self._playwright.chromium.launch(
                headless=self.headless, args=args
            )

        channels = BROWSER_CHANNELS if self.browser == "auto" else (self.browser,)

        for channel in channels:
            try:
                return await self._playwright.chromium.launch(
                    channel=channel, headless=self.headless, args=args
                )
            except Exception as error:
                logger.debug(f"Could not launch browser channel '{channel}': {error}")

        if self.browser != "auto":
            raise RuntimeError(f"Browser '{self.browser}' is not available")

        logger.info(
            "Using bundled Chromium (no proprietary codecs); "
            "install Chrome or use --browser to change this."
        )
        return await self._playwright.chromium.launch(headless=self.headless, args=args)

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._launch_browser()
        self._context = await self._browser.new_context(
            is_mobile=True,
            java_script_enabled=True,
        )

        stealth = Stealth(init_scripts_only=True)

        await stealth.apply_stealth_async(self._context)

        await load_state(self._context, SESSION_FILE)

        await self._set_profile()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await close_pages(self._context)
        await self._context.close()
        await self._browser.close()
        await self._playwright.stop()

    @property
    def context(self) -> BrowserContext:
        return self._context

    @property
    async def page(self) -> Page:
        return await self._context.new_page()

    @try_except_request
    async def login(self):
        logger.info("Please login, in the opened browser")
        logger.info("You have to login manually, you have 2 minutes to do it")

        SELECTOR = "h1.h1.f-text-34"

        try:
            page = await self.page
            await page.goto(LOGIN_URL)

            welcome_message = await page.wait_for_selector(
                SELECTOR,
                timeout=2 * 60 * 1000,
            )

            if not welcome_message:
                raise LoginError()

            self.authenticated = True
            await save_state(self.context, SESSION_FILE)
            logger.info("Logged in successfully")

        except Exception:
            raise LoginError()

        finally:
            await page.close()

    @try_except_request
    async def logout(self):
        SESSION_FILE.unlink(missing_ok=True)
        logger.info("Logged out successfully")

    @try_except_request
    @login_required
    async def fetch_unit(
        self,
        url: str,
        settings: RateLimitSettings | None = None,
        stats: ThrottleStats | None = None,
    ):
        return await collectors.fetch_unit(self.context, url, settings, stats)

    @try_except_request
    @login_required
    async def fetch_course(
        self,
        url: str,
        settings: RateLimitSettings | None = None,
        stats: ThrottleStats | None = None,
    ):
        return await collectors.fetch_course(self.context, url, settings, stats)

    @try_except_request
    @login_required
    async def fetch_bootcamp(
        self,
        url: str,
        settings: RateLimitSettings | None = None,
        stats: ThrottleStats | None = None,
    ):
        return await collectors.fetch_bootcamp(self.context, url, settings, stats)

    @try_except_request
    @login_required
    async def download(
        self,
        url: str,
        settings: RateLimitSettings | None = None,
        status_only: bool = False,
        retry_failed: bool = False,
        **kwargs,
    ):
        from pathlib import Path

        from .downloaders import download_bootcamp, download_course, download_unit
        from .models import TypeUnit
        from .state import RunState, find_state
        from .utils import is_bootcamp, is_course, is_lecture, is_quiz, is_video

        stats = ThrottleStats()

        if is_video(url) or is_lecture(url) or is_quiz(url):
            if status_only or retry_failed:
                logger.warning(
                    "--status and --retry-failed only apply to courses and bootcamps"
                )
                return

            unit = await self.fetch_unit(url, settings, stats)
            extension = ".mp4" if unit.type == TypeUnit.VIDEO else ".mhtml"
            await download_unit(
                self.context,
                unit,
                Path(unit.slug + extension),
                settings=settings,
                stats=stats,
                **kwargs,
            )

        elif is_course(url) or is_bootcamp(url):
            kind = "course" if is_course(url) else "bootcamp"
            run = find_state(url)

            if status_only:
                self._report_state(url, run)
                return

            if retry_failed:
                await self._retry_failures(url, run, settings, stats, **kwargs)

                if stats.has_events():
                    logger.info(stats.summary())
                return

            if (
                run is not None
                and run.completed()
                and run.outputs_present()
                and not kwargs.get("override", False)
            ):
                logger.info(
                    f"[{run.slug}] already completed, skipping "
                    "(use --override to redo)"
                )
                return

            if is_course(url):
                course = await self.fetch_course(url, settings, stats)

                if run is None:
                    run = RunState(url=url, kind=kind, slug=course.slug)

                await download_course(
                    self.context,
                    course,
                    settings=settings,
                    stats=stats,
                    state=run,
                    **kwargs,
                )

            else:
                bootcamp = await self.fetch_bootcamp(url, settings, stats)

                if run is None:
                    run = RunState(url=url, kind=kind, slug=bootcamp.slug)

                await download_bootcamp(
                    self.context,
                    bootcamp,
                    settings=settings,
                    stats=stats,
                    state=run,
                    **kwargs,
                )

        else:
            raise Exception(
                "Please provide a valid URL, either a video, lecture, "
                "course, or bootcamp."
            )

        if stats.has_events():
            logger.info(stats.summary())

    def _report_state(self, url: str, run) -> None:
        from .ratelimit import redact_url

        if run is None:
            logger.info(f"No saved state for {redact_url(url)}")
            return

        failures = run.failures()
        status = "completed" if run.completed() else "in progress"

        logger.info(
            f"[{run.slug}] {status}: {len(run.units)} units, "
            f"{len(failures)} pending failures"
        )

        for entry in failures:
            logger.info(f"  - {entry.path}: {entry.error or 'failed'}")

    async def _retry_failures(self, url, run, settings, stats, **kwargs) -> None:
        from pathlib import Path

        from .downloaders import download_unit
        from .models import TypeUnit, Unit, UnitOutcome
        from .ratelimit import redact_url
        from .state import save_state

        if run is None or not run.failures():
            logger.info(f"No pending failures for {redact_url(url)}")
            return

        for entry in list(run.failures()):
            unit = Unit(
                type=TypeUnit(entry.unit_type),
                name=Path(entry.path).stem,
                slug=Path(entry.path).stem,
                url=entry.url,
            )

            try:
                outcome = await download_unit(
                    self.context,
                    unit,
                    Path(entry.path),
                    settings=settings,
                    stats=stats,
                    **kwargs,
                )
            except AbortError:
                save_state(run)
                raise

            run.record(
                entry.path,
                unit,
                outcome or UnitOutcome(success=False, error="no outcome"),
            )
            save_state(run)

    @try_except_request
    async def set_cookies(self, path: Path):
        cookies = normalize_cookies(read_json(path))  # type: ignore
        await self.context.add_cookies(cookies)  # type: ignore
        await self._set_profile()
        await save_state(self.context, SESSION_FILE)

    @try_except_request
    async def _set_profile(self):
        SELECTOR = "h1.h1.f-text-34"
        TIMEOUT = 5 * 1000

        try:
            page = await self.page
            await page.goto(BASE_URL)

            welcome_message = await page.locator(SELECTOR).first.text_content(
                timeout=TIMEOUT
            )

            if welcome_message:
                self.authenticated = True
                logger.info(welcome_message)

        except Exception:
            pass

        finally:
            await page.close()
