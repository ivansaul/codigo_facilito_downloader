import hashlib
import json
import re
from pathlib import Path

YOUTUBE_ID_PATTERN = re.compile(
    r"(?:youtube\.com|youtube-nocookie\.com)/embed/(?P<embed>[A-Za-z0-9_-]{11})"
    r"|youtu\.be/(?P<short>[A-Za-z0-9_-]{11})"
    r"|youtube\.com/watch\?(?:[^\"'\s]*&)?v=(?P<watch>[A-Za-z0-9_-]{11})"
)


def extract_youtube_id(text: str) -> str | None:
    """
    Extract the 11-character video id from a YouTube URL or markup.

    :param str text: Text that may contain an embed, short or watch URL.
    :return str | None: The video id, or None if no valid URL is found.
    """
    if not text:
        return None

    match = YOUTUBE_ID_PATTERN.search(text)

    if not match:
        return None

    return match.group("embed") or match.group("short") or match.group("watch")


def read_json(path: str | Path) -> dict:
    """
    Read a JSON file and return its contents as a dictionary.

    :param str | Path path: path to the JSON file
    :return dict: dictionary containing the JSON data

    Example
    -------
    >>> read_json("data.json")
    {"key": "value"}
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str | Path, data: dict) -> None:
    """
    Write a dictionary to a JSON file.

    :param str | Path path: path to the JSON file
    :param dict data: dictionary to write
    :return None: None

    Example
    -------
    >>> write_json({"key": "value"}, "data.json")
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def clean_string(text: str) -> str:
    """
    Remove special characters from a string and strip it.

    :param str text: string to clean
    :return str: cleaned string

    Example
    -------
    >>> clean_string("   Hi:;<>?{}|"")
    "Hi"
    """
    pattern = r"[ºª]|[^\w\s]"
    return re.sub(pattern, "", text).strip()


def slugify(text: str) -> str:
    """
    Slugify a string, removing special characters and replacing
    spaces with hyphens.

    :param str text: string to convert
    :return str: slugified string

    Example
    -------
    >>> slugify(""Café! Frío?"")
    "cafe-frio"
    """
    from unidecode import unidecode

    return unidecode(clean_string(text)).lower().replace(" ", "-")


def hashify(input: str) -> str:
    """
    Generate a unique hash for a given string.

    :param str input: string to hash
    :return str: hash string

    Example
    -------
    >>> hashify("Hello, World!")
    "b109f81c07a71be02dbc28adac84f3a5df7e4be2b91329d1b0149d17bd6c92b3"
    """
    hash_object = hashlib.sha256(input.encode("utf-8"))
    return hash_object.hexdigest()


async def download_file(url: str, path: Path | str, overwrite: bool = False):
    """
    Download a file from a URL and save it to a path.

    :param str url: URL of the file to download
    :param Path | str path: path to save the file
    :param bool overwrite: overwrite existing file if exists (default: False)
    :return None: None
    :raises aiohttp.ClientError: For network-related errors
    :raises OSError: If there's an error writing to the file
    :raises Exception: For other errors

    Example
    -------
    >>> await download_file("https://example.com/file.txt", "file.txt")
    """
    import aiofiles  # type: ignore
    import aiohttp

    path = Path(path) if isinstance(path, str) else path

    if not overwrite and path.exists():
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(path, "wb") as file:
                    async for chunk in response.content.iter_chunked(1024):
                        await file.write(chunk)
        except aiohttp.ClientError:
            raise Exception(f"Network error downloading {url}")
        except OSError:
            raise Exception(f"Error saving to {path}")
        except Exception:
            raise Exception(f"Something went wrong downloading {url}")
