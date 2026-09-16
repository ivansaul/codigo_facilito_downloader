from facilito.errors import (
    AbortError,
    BaseError,
    LoginError,
    RateLimitError,
    RetryExhaustedError,
)


def test_abort_error_hierarchy():
    assert issubclass(AbortError, BaseError)
    assert issubclass(RateLimitError, AbortError)
    assert issubclass(RetryExhaustedError, RateLimitError)
    assert issubclass(RetryExhaustedError, AbortError)
    assert issubclass(RetryExhaustedError, BaseError)


def test_login_error_is_not_abort_error():
    assert not issubclass(LoginError, AbortError)


def test_abort_error_uses_docstring_as_default_message():
    assert str(AbortError()) == AbortError.__doc__


def test_retry_exhausted_error_fields():
    error = RetryExhaustedError(label="01_intro.mp4", attempts=4, reason="HTTP 429")

    assert error.label == "01_intro.mp4"
    assert error.attempts == 4
    assert error.reason == "HTTP 429"
    assert "01_intro.mp4" in str(error)
    assert "4" in str(error)
    assert "HTTP 429" in str(error)


def test_retry_exhausted_error_without_reason():
    error = RetryExhaustedError(label="clip", attempts=2)

    assert error.reason is None
    assert "clip" in str(error)
    assert "2" in str(error)
