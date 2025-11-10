import asyncio
from pathlib import Path

import typer
from typing_extensions import Annotated

from facilito import AsyncFacilito, Quality

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
    asyncio.run(
        _download(
            url,
            quality=quality,
            override=override,
            threads=threads,
        )
    )


async def _login():
    async with AsyncFacilito() as client:
        await client.login()


async def _logout():
    async with AsyncFacilito() as client:
        await client.logout()


async def _download(url: str, **kwargs):
    async with AsyncFacilito() as client:
        await client.download(url, **kwargs)


async def _set_cookies(path: Path):
    async with AsyncFacilito() as client:
        await client.set_cookies(path)
