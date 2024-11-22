import asyncio

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
            help="The URL of the course | video | lecture to download.",
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
):
    """
    Download a course | video | lecture from the given URL.

    Arguments:
        url: str - The URL of the course to download.

    Usage:
        facilito download <url>

    Example:
        facilito download https://codigofacilito.com/cursos/docker

        facilito download https://codigofacilito.com/videos/...

        facilito download https://codigofacilito.com/articulos/...
    """
    asyncio.run(
        _download(
            url,
            quality=quality,
            override=override,
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
