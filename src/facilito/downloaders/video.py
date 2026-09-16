import functools
import os
import platform
import re
import shutil
import tarfile
import zipfile
from pathlib import Path

from ..constants import APP_NAME, BASE_URL
from ..errors import AbortError
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

    version = "0.4.1"

    release_url = "https://github.com/clitic/vsd/releases/download/vsd-{version}/vsd-{version}-{bin}"

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
        ("windows", "amd64"): release_url.format(
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

            if ZIP_NAME.endswith(".zip"):
                with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
                    zip_ref.extractall(TMP_DIR_PATH)

            if ZIP_NAME.endswith(".tar.xz"):
                with tarfile.open(ZIP_PATH, "r:xz") as tar:
                    tar.extractall(TMP_DIR_PATH)

            for current_dir, _subdirs, files in os.walk(TMP_DIR_PATH):
                for file in files:
                    if file in ["vsd", "vsd.exe"]:
                        src = os.path.join(current_dir, file)
                        shutil.move(src, BIN_DIR_PATH)
        except Exception:
            logger.exception("Error downloading binary video downloader")
            ZIP_PATH.unlink(missing_ok=True)

    if VSD_BIN_PATH.exists():
        if not os.access(VSD_BIN_PATH, os.X_OK):
            os.chmod(VSD_BIN_PATH, 0o744)

        if "PATH" not in os.environ:
            os.environ["PATH"] = BIN_DIR_PATH.as_posix()

        elif BIN_DIR_PATH.as_posix() not in os.environ["PATH"]:
            os.environ["PATH"] = (
                BIN_DIR_PATH.as_posix() + os.pathsep + os.environ["PATH"]
            )

        return VSD_BIN_PATH

    # Fall back to a system-installed vsd binary
    system_vsd = shutil.which("vsd")

    if system_vsd:
        return Path(system_vsd)

    logger.error("vsd binary is not available")
    return None


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
    :param int threads: Number of threads to use (default: 10).
    """

    import asyncio
    import subprocess

    from ..ratelimit import (
        RateLimitSettings,
        RetryPolicy,
        RetrySignal,
        ThrottleStats,
        classify_vsd_error,
        parse_retry_after,
        redact_url,
        run_with_retry,
    )

    cookies = kwargs.get("cookies", None)
    override = kwargs.get("override", False)
    threads = kwargs.get("threads", 10)
    settings = kwargs.get("settings") or RateLimitSettings()
    stats = kwargs.get("stats") or ThrottleStats()

    path.parent.mkdir(parents=True, exist_ok=True)

    if not override and path.exists():
        logger.info(f"[{path.name}] already exists")
        return

    TMP_COOKIES_PATH = TMP_DIR_PATH / f"{hashify(url)}.json"

    if cookies:
        write_json(TMP_COOKIES_PATH, cookies)

    # Download vsd binary if not exists
    vsd_bin = await _download_vsd()

    if not vsd_bin:
        logger.error(f"Error downloading [{path.name}]: vsd binary is not available")
        return

    command = [
        vsd_bin.as_posix(),
        "save",
        url,
        "--directory",
        TMP_DIR_PATH.as_posix(),
        "--output",
        path.as_posix(),
        "--quality",
        quality.value,
        "--threads",
        str(threads),
    ]

    if cookies:
        command += ["--cookies", TMP_COOKIES_PATH.as_posix()]

    # The CDN enforces referer-based hotlink protection: without this header the
    # playlist requests return 403 and vsd reports "no playlists were found".
    command += ["--header", "Referer", f"{BASE_URL}/"]

    policy = RetryPolicy.from_settings(settings)

    logger.debug(f"Downloading [{path.name}] from {redact_url(url)}")

    def run_vsd():
        return subprocess.run(command, stderr=subprocess.PIPE, text=True)

    async def save():
        result = await asyncio.to_thread(run_vsd)

        detection = classify_vsd_error(
            result.returncode,
            result.stderr,
            block_detection_enabled=settings.block_detection_enabled,
        )

        if detection is None:
            return

        # A failed attempt can leave a partial file behind; remove it so it is
        # never mistaken for a completed download on the next attempt.
        if path.exists():
            path.unlink(missing_ok=True)

        retry_after = None

        if result.stderr:
            match = re.search(r"retry-after[:\s=]+(\S+)", result.stderr, re.IGNORECASE)

            if match:
                retry_after = parse_retry_after(match.group(1))

        reason = " ".join((result.stderr or "").split())[:200]
        reason = reason or f"vsd exited with {result.returncode}"

        raise RetrySignal(detection, reason, retry_after=retry_after)

    try:
        # TODO: Implement custom progress bar
        await run_with_retry(save, policy, stats, label=path.name)
    except AbortError:
        raise
    except Exception:
        logger.exception(f"Error downloading [{path.name}]")

    finally:
        if TMP_COOKIES_PATH.exists():
            TMP_COOKIES_PATH.unlink()
