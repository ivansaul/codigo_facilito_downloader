"""
Helpers
"""

import json
import os
import re
import subprocess
from typing import Any, Dict

from . import consts
from .models.video import Quality


def is_video_url(url: str) -> bool:
    """
    Checks if the provided url is a valid video url
    """
    pattern = re.compile(consts.VIDEO_URL_REGEX)
    return bool(pattern.match(url))


def is_course_url(url: str) -> bool:
    """
    Checks if the provided url is a valid course url
    """
    pattern = re.compile(consts.COURSE_URL_REGEX)
    return bool(pattern.match(url))


# TODO: implement error handling 👇
def to_netscape_string(cookie_data: list[dict]) -> str:
    """
    Convert cookies to Netscape cookie format.

    This function takes a list of cookie dictionaries and transforms them into
    a single string in Netscape cookie file format, which is commonly used by
    web browsers and other HTTP clients for cookie storage. The Netscape string
    can be used to programmatically interact with websites by simulating the
    presence of cookies that might be set during normal web browsing.

    Args:
        cookie_data (list of dict): A list of dictionaries where each dictionary
            represents a cookie. Each dictionary should have the following keys:
            - 'domain': The domain of the cookie.
            - 'expires': The expiration date of the cookie as a timestamp.
            - 'path': The path for which the cookie is valid.
            - 'secure': A boolean indicating if the cookie is secure.
            - 'name': The name of the cookie.
            - 'value': The value of the cookie.

    Returns:
        str: A string representing the cookie data in Netscape cookie file format.

    Example of Netscape cookie file format:
        .codigofacilito.com	TRUE	/	TRUE	0	CloudFront-Key-Pair-Id	APKAIAHLS7PK3GAUR2RQ
    """
    result = []
    for cookie in cookie_data:
        domain = cookie.get("domain", "")
        expiration_date = cookie.get("expires", 0)
        path = cookie.get("path", "")
        secure = cookie.get("secure", False)
        name = cookie.get("name", "")
        value = cookie.get("value", "")

        include_sub_domain = domain.startswith(".") if domain else False
        expiry = str(int(expiration_date)) if expiration_date > 0 else "0"

        result.append(
            [
                domain,
                str(include_sub_domain).upper(),
                path,
                str(secure).upper(),
                expiry,
                name,
                value,
            ]
        )

    return "\n".join("\t".join(cookie_parts) for cookie_parts in result)


def save_cookies_to_file(
    cookie_data: list[dict], file_path=consts.COOKIES_FILE
) -> None:
    """
    Save cookies to txt file
    """
    netscape_string = to_netscape_string(cookie_data)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# Netscape HTTP Cookie File\n")
        file.write("# http://www.netscape.com/newsref/std/cookie_spec.html\n")
        file.write("# This is a generated file!  Do not edit.\n")
        file.write(netscape_string)


def quality_to_dlp_format(quality: Quality) -> str:
    """
    Convert quality enum to string
    """
    height = quality.value
    match quality:
        case Quality.BEST:
            dl_format = "bv+ba/b"
        case Quality.WORST:
            dl_format = "wv+wa/w"
        case Quality.P1080 | Quality.P720 | Quality.P480 | Quality.P360:
            dl_format = f"bv[height={height}]+ba/b[height={height}]"
        case _:
            dl_format = "bv+ba/b"

    return dl_format


def read_json(path: str) -> Dict[str, Any]:
    """
    Read json file.

    Args:
    path (str): The file path to the json file that will be read.

    Returns:
    Dict[str, Any]: A dictionary containing the parsed JSON data.
    """
    with open(path, "r", encoding="utf-8") as file:
        content = json.load(file)
        return content


def write_json(data: Dict[str, Any], path: str) -> None:
    """
    Write the JSON data to a file.

    Args:
        data (Dict[str, Any]): The data to write to the file.
        path (str): The path to the file where the JSON data will be written.
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def clean_string(text: str) -> str:
    """
    This function cleans the input string by removing special
    characters and leading/trailing white spaces.

    Args:
        input_string (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    return re.sub(r'[<>:"/\\|?!¡¿º%&~ª*+=!"#$%&?¿¡[\]{}@]', "", text).strip()


def check_dir(path: str) -> None:
    """
    Check if a given directory path exists and create it if it does not.

    Args:
        path (str): The path to check and create if necessary.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def is_ffmpeg_installed() -> bool:
    """
    Check if ffmpeg is installed.

    Returns:
        bool: True if ffmpeg is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False
