from pathlib import Path

from playwright.async_api import BrowserContext

from ..collectors import fetch_video
from ..models import TypeUnit, Unit
from ..utils import save_page
from .video import download_video


async def download_unit(context: BrowserContext, unit: Unit, path: Path, **kwargs):
    """
    Download a Unit.

    :param BrowserContext context: Playwright context.
    :param Unit unit: Unit model to download.
    :param Path path: Path to save the video.

    :param Quality quality: Quality of the video (default: Quality.MAX).
    :param bool override: Override existing file if exists (default: False).
    :param int threads: Number of threads to use (default: 10).
    """

    if unit.type == TypeUnit.VIDEO:
        video = await fetch_video(context, unit.url)
        await download_video(
            video.url,
            path=path,
            cookies=await context.cookies(),
            **kwargs,
        )  # type: ignore

    if unit.type == TypeUnit.LECTURE:
        await save_page(context, unit.url, path)
