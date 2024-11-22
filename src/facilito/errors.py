class BaseError(Exception):
    """Base class for custom errors."""

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)


class LoginError(BaseError):
    """Login failed"""


class VideoError(BaseError):
    """Video, cannot be fetched or parsed properly."""


class UnitError(BaseError):
    """Unit, cannot be fetched or parsed properly."""


class CourseError(BaseError):
    """Course, cannot be fetched or parsed properly."""
