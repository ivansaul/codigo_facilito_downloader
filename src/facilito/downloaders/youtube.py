import asyncio
from pathlib import Path

from ..errors import AbortError
from ..logger import logger
from ..models import Quality, UnitOutcome
from ..ratelimit import (
    RateLimitSettings,
    RetryPolicy,
    RetrySignal,
    ThrottleStats,
    classify_youtube_error,
    run_with_retry,
)
from .video import ffmpeg_required

_HEIGHT_BY_QUALITY = {"1080p": 1080, "720p": 720, "480p": 480, "360p": 360}


def quality_to_format(quality: Quality) -> str:
    """
    Map the CLI quality to a yt-dlp format selection.

    Picks the best quality at or below the requested height; if none is below,
    falls back to the best available.
    """
    if quality == Quality.MAX:
        return "bestvideo*+bestaudio/best"

    if quality == Quality.MIN:
        return "worstvideo*+worstaudio/worst"

    height = _HEIGHT_BY_QUALITY[quality.value]
    return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"


@ffmpeg_required
async def download_youtube(
    url: str,
    path: Path,
    quality: Quality = Quality.MAX,
    **kwargs,
) -> UnitOutcome:
    """
    Download an embedded YouTube video to path.

    :param str url: YouTube watch URL.
    :param Path path: Path to save the video.
    :param Quality quality: Quality of the video (default: Quality.MAX).
    :param bool override: Override existing file if exists (default: False).
    """

    settings = kwargs.get("settings") or RateLimitSettings()
    stats = kwargs.get("stats") or ThrottleStats()

    path.parent.mkdir(parents=True, exist_ok=True)

    if not kwargs.get("override", False) and path.exists():
        logger.info(f"[{path.name}] already exists")
        return UnitOutcome(success=True, provider="youtube")

    try:
        import yt_dlp
    except ImportError:
        logger.error(
            "yt-dlp is not installed, cannot download embedded videos; "
            "install it with: pip install yt-dlp"
        )
        return UnitOutcome(
            success=False, error="yt-dlp is not installed", provider="youtube"
        )

    policy = RetryPolicy.from_settings(settings)

    def run_download():
        options = {
            "format": quality_to_format(quality),
            "outtmpl": path.as_posix(),
            "merge_output_format": "mp4",
            "quiet": True,
            "noprogress": True,
            "no_warnings": True,
            "noplaylist": True,
            "retries": 1,
            "fragment_retries": 1,
            "overwrites": True,
        }

        logger.debug(f"YouTube format: {options['format']}")

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])

    async def save():
        try:
            await asyncio.to_thread(run_download)
        except Exception as error:
            # A failed attempt can leave a partial file behind.
            if path.exists():
                path.unlink(missing_ok=True)

            message = str(error)
            raise RetrySignal(classify_youtube_error(message), message)

    try:
        logger.info(f"Downloading YouTube video [{path.name}]")
        await run_with_retry(save, policy, stats, label=path.name)
    except AbortError:
        raise
    except Exception as error:
        logger.exception(f"Error downloading [{path.name}]")
        return UnitOutcome(success=False, error=str(error), provider="youtube")

    return UnitOutcome(success=True, provider="youtube")
