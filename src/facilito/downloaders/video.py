import functools
import os
import platform
import shutil
import tarfile
import zipfile
from pathlib import Path

from ..constants import APP_NAME
from ..helpers import download_file, hashify, write_json
from ..logger import logger
from ..models import Quality

TMP_DIR_PATH = Path(APP_NAME) / ".tmp"
BIN_DIR_PATH = Path(APP_NAME) / ".bin"

TMP_DIR_PATH.mkdir(parents=True, exist_ok=True)
BIN_DIR_PATH.mkdir(parents=True, exist_ok=True)


async def _download_vsd():
    system = platform.system().lower()  # linux, darwin, windows
    arch = platform.machine().lower()  # x86_64, arm64

    version = "0.3.2"

    release_url = (
        "https://github.com/clitic/vsd/releases/download/{version}/vsd-{version}-{bin}"
    )

    binary_urls = {
        ("linux", "x86_64"): release_url.format(
            version=version, bin="x86_64-unknown-linux-musl.tar.xz"
        ),
        ("linux", "arm64"): release_url.format(
            version=version, bin="aarch64-unknown-linux-musl.tar.xz"
        ),
        ("darwin", "x86_64"): release_url.format(
            version=version, bin="x86_64-apple-darwin.tar.xz"
        ),
        ("darwin", "arm64"): release_url.format(
            version=version, bin="aarch64-apple-darwin.tar.xz"
        ),
        ("windows", "x86_64"): release_url.format(
            version=version, bin="x86_64-pc-windows-msvc.zip"
        ),
        ("windows", "arm64"): release_url.format(
            version=version, bin="aarch64-pc-windows-msvc.zip"
        ),
    }

    binary_url = binary_urls.get((system, arch))
    if not binary_url:
        logger.error(f"Unsupported platform: {system} {arch}")
        return

    ZIP_NAME = binary_url.split("/")[-1]
    ZIP_PATH = TMP_DIR_PATH / ZIP_NAME

    if system == "windows":
        VSD_BIN_PATH = BIN_DIR_PATH / "vsd.exe"
    else:
        VSD_BIN_PATH = BIN_DIR_PATH / "vsd"

    if not VSD_BIN_PATH.exists():
        try:
            logger.info("Downloading video downloader binary")
            await download_file(binary_url, ZIP_PATH)
        except Exception:
            logger.error("Error downloading binary video downloader")
            return

        if ZIP_NAME.endswith(".zip"):
            with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(TMP_DIR_PATH)

        if ZIP_NAME.endswith(".tar.xz"):
            with tarfile.open(ZIP_PATH, "r:xz") as tar:
                tar.extractall(TMP_DIR_PATH)

        for dir, subdirs, files in os.walk(TMP_DIR_PATH):
            for file in files:
                if file in ["vsd", "vsd.exe"]:
                    src = os.path.join(dir, file)
                    shutil.move(src, BIN_DIR_PATH)

        if not os.access(VSD_BIN_PATH, os.X_OK):
            os.chmod(VSD_BIN_PATH, 0o744)

    if "PATH" not in os.environ:
        os.environ["PATH"] = BIN_DIR_PATH.as_posix()

    elif BIN_DIR_PATH.as_posix() not in os.environ["PATH"]:
        os.environ["PATH"] = BIN_DIR_PATH.as_posix() + os.pathsep + os.environ["PATH"]


def ffmpeg_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not shutil.which("ffmpeg"):
            logger.error("ffmpeg is not installed")
            return
        return await func(*args, **kwargs)

    return wrapper


@ffmpeg_required
async def download_video(
    url: str,
    path: Path,
    quality: Quality = Quality.MAX,
    **kwargs,
):
    """
    Download a video from a URL.

    :param str url: URL of the video.
    :param Path path: Path to save the video.
    :param Quality quality: Quality of the video (default: Quality.MIN).

    :param list[dic] cookies: Cookies for authentication (default: None).
    :param bool override: Override existing file if exists (default: False).
    """

    import subprocess

    cookies = kwargs.get("cookies", None)
    override = kwargs.get("override", False)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not override and path.exists():
        logger.info(f"[{path.name}] already exists")
        return

    TMP_COOKIES_PATH = TMP_DIR_PATH / f"{hashify(url)}.json"

    write_json(TMP_COOKIES_PATH, cookies)

    command = [
        "vsd",
        "save",
        url,
        "--cookies" if cookies else "",
        TMP_COOKIES_PATH.as_posix() if cookies else "",
        "--directory",
        TMP_DIR_PATH.as_posix(),
        "--output",
        path.as_posix(),
        "--quality",
        quality.value,
        "--skip-prompts",
    ]

    # Download vsd binary if not exists
    await _download_vsd()

    try:
        # TODO: Implement custom progress bar
        subprocess.run(command)
    except Exception:
        logger.exception(f"Error downloading [{path.name}]")

    finally:
        if TMP_COOKIES_PATH.exists():
            TMP_COOKIES_PATH.unlink()
