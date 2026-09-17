from pathlib import Path

from playwright.async_api import BrowserContext

from ..collectors import fetch_video
from ..models import TypeUnit, Unit, UnitOutcome, VideoProvider
from ..utils import save_page
from .video import download_video
from .youtube import download_youtube

FFMPEG_ERROR = "ffmpeg is not installed"


async def download_unit(
    context: BrowserContext, unit: Unit, path: Path, **kwargs
) -> UnitOutcome:
    """
    Download a Unit and report whether it succeeded.

    :param BrowserContext context: Playwright context.
    :param Unit unit: Unit model to download.
    :param Path path: Path to save the video.

    :param Quality quality: Quality of the video (default: Quality.MAX).
    :param bool override: Override existing file if exists (default: False).
    :param int threads: Number of threads to use (default: 10).
    """

    if unit.type == TypeUnit.VIDEO:
        settings = kwargs.get("settings")
        stats = kwargs.get("stats")

        video = await fetch_video(context, unit.url, settings, stats)

        if video.provider == VideoProvider.YOUTUBE:
            outcome = await download_youtube(video.url, path=path, **kwargs)
            return outcome or UnitOutcome(
                success=False, error=FFMPEG_ERROR, provider="youtube"
            )

        outcome = await download_video(
            video.url,
            path=path,
            cookies=await context.cookies(),
            **kwargs,
        )  # type: ignore

        return outcome or UnitOutcome(success=False, error=FFMPEG_ERROR, provider="hls")

    await save_page(
        context,
        unit.url,
        path,
        settings=kwargs.get("settings"),
        stats=kwargs.get("stats"),
    )

    return UnitOutcome(success=True, provider="page")
