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


class AbortError(BaseError):
    """Run must stop; must not be swallowed."""


class RateLimitError(AbortError):
    """Rate limit or anti-bot challenge detected."""


class RetryExhaustedError(RateLimitError):
    """Transient failures persisted after max_retries."""

    def __init__(
        self,
        label: str,
        attempts: int,
        reason: str | None = None,
        message: str | None = None,
    ):
        self.label = label
        self.attempts = attempts
        self.reason = reason

        detail = f"Giving up on {label} after {attempts} attempts"

        if reason:
            detail += f": {reason}"

        super().__init__(message or detail)
