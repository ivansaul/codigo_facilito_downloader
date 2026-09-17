import asyncio
import functools
import weakref
from pathlib import Path

from playwright.async_api import BrowserContext, Page

from .errors import AbortError, UnitError
from .helpers import read_json, write_json
from .logger import logger
from .models import TypeUnit
from .ratelimit import RateLimitSettings, ThrottleStats, throttled_goto

_SHARED_PAGES: weakref.WeakKeyDictionary[BrowserContext, dict[str, Page]] = (
    weakref.WeakKeyDictionary()
)


def _is_closed(page: Page) -> bool:
    is_closed = getattr(page, "is_closed", None)
    return bool(is_closed()) if callable(is_closed) else False


async def acquire_page(context: BrowserContext, slot: str = "main") -> Page:
    """
    Return a page reused across the whole run for the given context.

    Opening a new page per unit makes the browser window reappear and steal
    focus on every unit; reusing one page per slot avoids that.
    """
    slots = _SHARED_PAGES.get(context)

    if slots is None:
        slots = {}
        _SHARED_PAGES[context] = slots

    page = slots.get(slot)

    if page is not None and not _is_closed(page):
        return page

    page = await context.new_page()
    slots[slot] = page
    return page


async def close_pages(context: BrowserContext) -> None:
    """Close every page reused for a context; call when the context ends."""
    slots = _SHARED_PAGES.pop(context, {})

    for page in slots.values():
        try:
            if not _is_closed(page):
                await page.close()
        except Exception:
            pass


def login_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from .async_api import AsyncFacilito

        self = args[0]
        if not isinstance(self, AsyncFacilito):
            logger.error(f"{login_required.__name__} can only decorate Facilito class.")
            return
        if not self.authenticated:
            logger.error("Login first!")
            return
        return await func(*args, **kwargs)

    return wrapper


def try_except_request(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AbortError:
            raise
        except Exception as e:
            if str(e):
                logger.exception(e)
        return

    return wrapper


async def save_state(context: BrowserContext, path: Path | None = None):
    if path is None:
        path = Path.cwd() / "state.json"

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    cookies = await context.cookies()
    write_json(path, cookies)  # type: ignore


async def load_state(context: BrowserContext, path: Path) -> None:
    if not path.exists():
        return
    cookies = read_json(path)
    await context.add_cookies(cookies)  # type: ignore


async def progressive_scroll(
    page: Page, time: float = 3, delay: float = 0.1, steps: int = 250
):
    delta, total_time = 0.0, 0.0
    while total_time < time:
        await asyncio.sleep(delay)
        await page.mouse.wheel(0, steps)
        delta += steps
        total_time += delay


@try_except_request
async def save_page(
    context: BrowserContext,
    src: str | Page,
    path: str | Path = "source.mhtml",
    settings: RateLimitSettings | None = None,
    stats: ThrottleStats | None = None,
):
    EXCEPTION = Exception(f"Error saving page as mhtml {path}")

    try:
        if isinstance(src, str):
            page = await acquire_page(context)
            await throttled_goto(
                page,
                src,
                settings or RateLimitSettings(),
                stats=stats or ThrottleStats(),
            )
        else:
            page = src

        await progressive_scroll(page)

        client = await page.context.new_cdp_session(page)
        response = await client.send("Page.captureSnapshot")

        with open(path, "w", encoding="utf-8", newline="\n") as file:
            file.write(response["data"])

    except AbortError:
        raise
    except Exception:
        raise EXCEPTION


def is_video(url: str) -> bool:
    """
    Check if a URL is a video.

    :param str url: URL to check.
    :return bool: True if the URL is a video, False otherwise.

    Example
    -------
    >>> is_video("https: ..../videos/...")
    True
    """
    return "/videos/" in url


def is_lecture(url: str) -> bool:
    """
    Check if a URL is a lecture.

    :param str url: URL to check.
    :return bool: True if the URL is a lecture, False otherwise.

    Example
    -------
    >>> is_lecture("https: ..../articulos/...")
    True
    """
    return "/articulos/" in url


def is_course(url: str) -> bool:
    """
    Check if a URL is a course.

    :param str url: URL to check.
    :return bool: True if the URL is a course, False otherwise.

    Example
    -------
    >>> is_course("https: ..../cursos/...")
    True
    """
    return "/cursos/" in url


def is_bootcamp(url: str) -> bool:
    """
    Check if a URL is a bootcamp.

    :param str url: URL to check.
    :return bool: True if the URL is a bootcamp, False otherwise.

    Example
    -------
    >>> is_bootcamp("https://codigofacilito.com/programas/...")
    True
    """
    return "/programas/" in url


def is_quiz(url: str) -> bool:
    """
    Check if a URL is a quiz.

    :param str url: URL to check.
    :return bool: True if the URL is a quiz, False otherwise.

    Example
    -------
    >>> is_quiz("https: ..../quizzes/...")
    True
    """
    return "/quizzes/" in url


def get_unit_type(url: str) -> TypeUnit:
    """
    Get the type of a unit from its URL.

    :param str url: URL of the unit.
    :return TypeUnit: Type of the unit.
    :raises UnitError: If the unit type is not recognized.

    Example
    -------
    >>> get_unit_type("https: ..../videos/...")
    TypeUnit.VIDEO
    """

    if is_video(url):
        return TypeUnit.VIDEO

    if is_lecture(url):
        return TypeUnit.LECTURE

    if is_quiz(url):
        return TypeUnit.QUIZ

    raise UnitError()


def normalize_cookies(cookies: list[dict]) -> list[dict]:
    """
    Normalize cookies to a common format.

    :param list[dict] cookies: List of cookies to normalize.
    :return list[dict]: Normalized list of cookies.
    """
    import copy

    same_site_valid_values = {"Lax", "Strict", "None"}
    same_site_key = "sameSite"

    cookies = copy.deepcopy(cookies)
    for cookie in cookies:
        same_site = cookie.get(same_site_key, "None")
        same_site = same_site.replace("unspecified", "Lax").capitalize()
        same_site = same_site if same_site in same_site_valid_values else "None"
        cookie[same_site_key] = same_site

    return cookies
