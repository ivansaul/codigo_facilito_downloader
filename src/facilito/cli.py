import asyncio
from pathlib import Path

import typer
from typing_extensions import Annotated

from facilito import AsyncFacilito, Quality
from facilito.config import resolve_settings
from facilito.constants import BROWSER_CHOICES, WINDOW_CHOICES
from facilito.errors import AbortError
from facilito.logger import logger

app = typer.Typer(rich_markup_mode="rich")


@app.command()
def login():
    """
    Open a browser window to Login to Codigo Facilito.

    Usage:
        facilito login
    """
    asyncio.run(_login())


@app.command()
def set_cookies(
    path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="Path to cookies.json",
            show_default=False,
        ),
    ],
):
    """
    Login to Codigo Facilito using your cookies.

    Usage:
        facilito set-cookies cookies.json
    """
    asyncio.run(_set_cookies(path))


@app.command()
def logout():
    """
    Delete the Facilito session from the local storage.

    Usage:
        facilito logout
    """
    asyncio.run(_logout())


@app.command()
def download(
    url: Annotated[
        str,
        typer.Argument(
            help="The URL of the bootcamp | course | video | lecture to download.",
            show_default=False,
        ),
    ],
    quality: Annotated[
        Quality,
        typer.Option(
            "--quality",
            "-q",
            help="The quality of the video to download.",
            show_default=True,
        ),
    ] = Quality.MAX,
    override: Annotated[
        bool,
        typer.Option(
            "--override",
            "-w",
            help="Override existing file if exists.",
            show_default=True,
        ),
    ] = False,
    threads: Annotated[
        int,
        typer.Option(
            "--threads",
            "-t",
            min=1,
            max=16,
            help="Number of threads to use.",
            show_default=True,
        ),
    ] = 10,
    request_delay: Annotated[
        float | None,
        typer.Option(
            "--request-delay",
            help=(
                "Base delay in seconds between page requests "
                "(scraping/MHTML). 0 disables pacing."
            ),
            show_default="0.0",
        ),
    ] = None,
    request_jitter: Annotated[
        float | None,
        typer.Option(
            "--request-jitter",
            help=(
                "Extra random jitter in seconds added to --request-delay; "
                "actual wait is delay + U(0, jitter)."
            ),
            show_default="0.0",
        ),
    ] = None,
    download_delay: Annotated[
        float | None,
        typer.Option(
            "--download-delay",
            help=(
                "Delay in seconds between consecutive video downloads. "
                "0 disables pacing."
            ),
            show_default="0.0",
        ),
    ] = None,
    retry: Annotated[
        bool | None,
        typer.Option(
            "--retry/--no-retry",
            help=(
                "Retry transient failures (429, 5xx, timeouts) "
                "with exponential backoff."
            ),
            show_default="True",
        ),
    ] = None,
    max_retries: Annotated[
        int | None,
        typer.Option(
            "--max-retries",
            help="Maximum retries after a failed attempt. 0 disables retries.",
            show_default="3",
        ),
    ] = None,
    retry_base_delay: Annotated[
        float | None,
        typer.Option(
            "--retry-base-delay",
            help="Base wait in seconds for the first retry; doubles per attempt.",
            show_default="1.0",
        ),
    ] = None,
    retry_max_delay: Annotated[
        float | None,
        typer.Option(
            "--retry-max-delay",
            help="Maximum wait in seconds for a single computed backoff.",
            show_default="30.0",
        ),
    ] = None,
    retry_after_max: Annotated[
        float | None,
        typer.Option(
            "--retry-after-max",
            help=(
                "Maximum seconds to honor a server Retry-After value; "
                "longer waits are capped with a warning."
            ),
            show_default="60.0",
        ),
    ] = None,
    block_detection: Annotated[
        bool | None,
        typer.Option(
            "--block-detection/--no-block-detection",
            help=(
                "Detect rate-limit/challenge responses "
                "(HTTP 429, Cloudflare 403) and back off."
            ),
            show_default="True",
        ),
    ] = None,
    config_path: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Path to the rate-limiting config file (JSON).",
            show_default="Facilito/config.json",
        ),
    ] = None,
    browser: Annotated[
        str | None,
        typer.Option(
            "--browser",
            help=(
                "Browser to launch: auto (Chrome/Edge if available, else "
                "bundled Chromium), chrome, msedge or chromium."
            ),
            show_default="auto",
        ),
    ] = None,
    window: Annotated[
        str | None,
        typer.Option(
            "--window",
            help=(
                "Browser window mode: offscreen (default, no popup), "
                "visible or headless (may be blocked by Cloudflare)."
            ),
            show_default="offscreen",
        ),
    ] = None,
    status_only: Annotated[
        bool,
        typer.Option(
            "--status",
            help=("Show saved progress and pending failures for the URL, then exit."),
        ),
    ] = False,
    retry_failed: Annotated[
        bool,
        typer.Option(
            "--retry-failed",
            help="Retry only the recorded failures, without traversing the course.",
        ),
    ] = False,
):
    """
    Download a bootcamp | course | video | lecture from the given URL.

    Arguments:
        url: str - The URL of the bootcamp, course, video, or lecture to download.

    Usage:
        facilito download <url>

    Examples:
        facilito download https://codigofacilito.com/programas/ingles-conversacional

        facilito download https://codigofacilito.com/cursos/docker

        facilito download https://codigofacilito.com/videos/...

        facilito download https://codigofacilito.com/articulos/...
    """
    cli_overrides = {
        "request_delay": request_delay,
        "request_jitter": request_jitter,
        "download_delay": download_delay,
        "retry_enabled": retry,
        "max_retries": max_retries,
        "retry_base_delay": retry_base_delay,
        "retry_max_delay": retry_max_delay,
        "retry_after_max": retry_after_max,
        "block_detection_enabled": block_detection,
    }

    settings = resolve_settings(cli_overrides, config_path)

    if browser is not None and browser not in BROWSER_CHOICES:
        raise typer.BadParameter(
            f"Invalid browser '{browser}'. "
            f"Choose one of: {', '.join(BROWSER_CHOICES)}."
        )

    if window is not None and window not in WINDOW_CHOICES:
        raise typer.BadParameter(
            f"Invalid window '{window}'. Choose one of: {', '.join(WINDOW_CHOICES)}."
        )

    if retry_failed and override:
        raise typer.BadParameter("--retry-failed cannot be combined with --override.")

    asyncio.run(
        _download(
            url,
            quality=quality,
            override=override,
            threads=threads,
            settings=settings,
            browser=browser,
            window=window,
            status_only=status_only,
            retry_failed=retry_failed,
        )
    )


async def _login():
    async with AsyncFacilito(window="visible") as client:
        await client.login()


async def _logout():
    async with AsyncFacilito() as client:
        await client.logout()


async def _download(url: str, **kwargs):
    browser = kwargs.pop("browser", None)
    window = kwargs.pop("window", None)

    async with AsyncFacilito(browser=browser, window=window) as client:
        try:
            await client.download(url, **kwargs)

        except AbortError as error:
            logger.error(
                f"Aborting run: {error}. "
                "Try increasing --download-delay or lowering --threads."
            )
            raise typer.Exit(code=1)


async def _set_cookies(path: Path):
    async with AsyncFacilito() as client:
        await client.set_cookies(path)
