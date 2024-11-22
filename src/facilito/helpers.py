import hashlib
import json
import re
from pathlib import Path


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
