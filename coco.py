"""
Codigo Facilito cli tool
"""

from typing import Annotated

import typer
from rich import print as tprint
from rich.console import Console
from rich.table import Table

from facilito import consts, helpers  # type: ignore
from facilito.core import Client  # type: ignore
from facilito.errors import CourseError, DownloadError, VideoError  # type: ignore
from facilito.models.video import Quality  # type: ignore
from facilito.utils.logger import cli_logger  # type: ignore

app = typer.Typer(
    rich_markup_mode="markdown",
    epilog="Made with :heart: in [ivansaul](https://github.com/ivansaul)",
)


@app.command()
def download(
    url: Annotated[
        str,
        typer.Option(prompt=True),
    ],
    quality: Quality = typer.Option(
        prompt=True,
        default=Quality.BEST.value,
        prompt_required=True,
    ),
    headless: bool = False,
):
    """
    Downloads [VIDEO|COURSE] from the provided URL.

    By default, it downloads the best quality video.
    """

    if not helpers.is_ffmpeg_installed():
        tprint(
            "[bold red]Error! [/bold red][bold magenta]ffmpeg is not installed.[/bold magenta]"
        )
        tprint(
            f"[bold magenta]Please [link={consts.FFMPEG_URL}]install[/link] it![/bold magenta]"
        )
        raise typer.Exit()

    if helpers.is_video_url(url):
        with Client(headless=headless) as client:
            tprint("⠹ Processing...")
            try:
                video = client.video(url)
            except VideoError as e:
                tprint("✗ Unable to download the video.")
                raise typer.Exit() from e

            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    tprint("⠹ Downloading...")
                    tprint("⠹", video.title, " ...")
                    client.refresh_cookies()
                    video.download(quality=quality)
                except DownloadError:
                    if attempt < max_retries:
                        tprint("⠹ An error occurred while downloading :(")
                        tprint("⠹ Retrying...")
                    else:
                        tprint("✗ Unable to download the video.")
                        break

                else:
                    tprint("✓ Done!")
                    break
        raise typer.Exit()

    if helpers.is_course_url(url):
        with Client(headless=headless) as client:
            tprint("⠹ Processing...")

            try:
                course = client.course(url)
                course_title = helpers.clean_string(course.title)
                course_sections = course.sections
                # Course Details Table
                console = Console()
                title_table = Table(course_title)
                console.print(title_table)
                sections_table = Table("Sections", "Videos")
                for section in course_sections:
                    sections_table.add_row(
                        section.title,
                        str(len(section.videos_url)),
                    )
                console.print(sections_table)
            except CourseError as e:
                tprint("✗ Unable to download the course.")
                raise typer.Exit() from e

            # Confirm download
            confirm_download = typer.confirm("Would you like to download?")
            if not confirm_download:
                raise typer.Exit()

            # iterate over sections
            course_sections = course.sections
            for pfx_s, section in enumerate(course_sections, start=1):
                section_title = helpers.clean_string(section.title)
                section_videos = section.videos_url
                for pfx_v, video_url in enumerate(section_videos, start=1):
                    try:
                        video = client.video(video_url)
                    except VideoError as e:
                        tprint("✗ Unable to fetch the video details.")
                        message = f"[SECTION] {section_title} [VIDEO] {video_url}"
                        cli_logger.error(message)
                        continue
                    max_retries = 5
                    for attempt in range(1, max_retries + 1):
                        try:
                            tprint("⠹ Downloading...")
                            tprint("⠹", video.title, " ...")
                            client.refresh_cookies()
                            # Download directory path
                            dir_path = f"{consts.DOWNLOADS_DIR}/{course_title}/{pfx_s:02d}. {section_title}"
                            video.download(
                                quality=quality,
                                dir_path=dir_path,
                                prefix_name=f"{pfx_v:02d}. ",
                            )
                        except DownloadError:
                            if attempt < max_retries:
                                tprint("⠹ An error occurred while downloading :(")
                                tprint("⠹ Retrying ...")
                            else:
                                tprint("✗ Unable to download the video.")
                                break
                        else:
                            tprint("✓ Done!")

        raise typer.Exit()

    tprint("[bold red]Error![/bold red] Thats not a valid [VIDEO|COURSE] URL")
    raise typer.Exit()


@app.command()
def login():
    """
    Authenticates a user with the given email and password.
    """
    while True:
        email = typer.prompt("What's your email?")
        confirm_email = typer.prompt("Confirm your email?")
        if email == confirm_email:
            break

        tprint(
            "[bold red]Error![/bold red] [magenta]The two entered values do not match.[/magenta]"
        )

    while True:
        password = typer.prompt("What's your password?", hide_input=False)
        confirm_password = typer.prompt("Confirm your password?", hide_input=False)
        if password == confirm_password:
            break

        tprint(
            "[bold red]Error![/bold red] [magenta]The two entered values do not match.[/magenta]"
        )

    # save credentials
    user = {"email": email, "password": password}
    helpers.write_json(data=user, path=consts.CONFIG_FILE)


if __name__ == "__main__":
    app()
