"""Helpers for collectors"""

from ..errors import UnitError
from ..models import TypeUnit


def is_video(url: str) -> bool:
    return "/videos/" in url


def is_lecture(url: str) -> bool:
    return "/articulos/" in url


def get_unit_type(url: str) -> TypeUnit:
    if is_video(url):
        return TypeUnit.VIDEO
    if is_lecture(url):
        return TypeUnit.LECTURE

    raise UnitError()
