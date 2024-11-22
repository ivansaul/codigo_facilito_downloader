import asyncio
import functools
from pathlib import Path

from playwright.async_api import BrowserContext, Page

from .helpers import read_json, write_json
from .logger import logger


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
    context: BrowserContext, src: str | Page, path: str | Path = "source.mhtml"
):
    EXCEPTION = Exception(f"Error saving page as mhtml {path}")

    try:
        if isinstance(src, str):
            page = await context.new_page()
            await page.goto(src)
        else:
            page = src

        await progressive_scroll(page)

        client = await page.context.new_cdp_session(page)
        response = await client.send("Page.captureSnapshot")

        with open(path, "w", encoding="utf-8", newline="\n") as file:
            file.write(response["data"])

    except Exception:
        raise EXCEPTION

    finally:
        if isinstance(src, str):
            await page.close()
