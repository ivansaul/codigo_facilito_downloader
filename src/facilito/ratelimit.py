import asyncio
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import timezone
from email.utils import parsedate_to_datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .errors import LoginError, RetryExhaustedError
from .logger import logger

Sleep = Callable[[float], Awaitable[None]]

_RNG = random.Random()


class RateLimitSettings(BaseModel):
    """Validated configuration for rate-limiting prevention."""

    model_config = ConfigDict(extra="forbid")

    request_delay: float = Field(default=0.0, ge=0.0, le=600.0)
    request_jitter: float = Field(default=0.0, ge=0.0, le=600.0)
    download_delay: float = Field(default=0.0, ge=0.0, le=600.0)
    retry_enabled: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_base_delay: float = Field(default=1.0, ge=0.1, le=60.0)
    retry_max_delay: float = Field(default=30.0, ge=0.1, le=300.0)
    retry_after_max: float = Field(default=60.0, ge=1.0, le=600.0)
    block_detection_enabled: bool = True

    @model_validator(mode="after")
    def _check_bounds(self):
        if self.retry_max_delay < self.retry_base_delay:
            raise ValueError(
                "retry_max_delay must be greater or equal to retry_base_delay"
            )

        return self


class Detection(str, Enum):
    """Classification of a failed operation for the retry loop."""

    RETRYABLE_THROTTLE = "retryable_throttle"
    RETRYABLE_TRANSIENT = "retryable_transient"
    AUTH_FAILURE = "auth_failure"
    FATAL = "fatal"


class RetrySignal(Exception):
    """Internal signal feeding a classified failure into the retry loop."""

    def __init__(
        self,
        detection: Detection,
        reason: str = "",
        retry_after: float | None = None,
    ):
        self.detection = detection
        self.reason = reason
        self.retry_after = retry_after
        super().__init__(reason or detection.value)


@dataclass
class ThrottleStats:
    """Accumulated rate-limiting events for a single run."""

    retries: int = 0
    throttles: int = 0
    waits: int = 0
    cap_hits: int = 0
    exhausted: int = 0

    def has_events(self) -> bool:
        return any(
            (self.retries, self.throttles, self.waits, self.cap_hits, self.exhausted)
        )

    def summary(self) -> str:
        return (
            "Rate limiting summary: "
            f"retries={self.retries} throttles={self.throttles} "
            f"waits={self.waits} capped={self.cap_hits} "
            f"exhausted={self.exhausted}"
        )


class RetryPolicy(BaseModel):
    """Retry/backoff policy derived from user settings."""

    enabled: bool = True
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    retry_after_max: float = 60.0
    jitter: bool = True

    @classmethod
    def from_settings(cls, settings: RateLimitSettings) -> "RetryPolicy":
        return cls(
            enabled=settings.retry_enabled,
            max_retries=settings.max_retries,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
            retry_after_max=settings.retry_after_max,
        )


CHALLENGE_BODY_MARKERS = (
    "cf-chl",
    "challenge-platform",
    "__cf_chl",
    "cf_chl_opt",
    "just a moment",
    "attention required",
    "checking your browser",
    "enable javascript and cookies",
)

AUTH_URL_MARKERS = ("/users/sign_in",)
AUTH_BODY_MARKERS = ("new_user",)

_VSD_THROTTLE_PATTERNS = (
    r"\b429\b",
    r"too many requests",
    r"rate.?limit",
    r"retry-after",
)
_VSD_CHALLENGE_PATTERNS = (r"forbidden", r"cloudflare", r"challenge")
_VSD_AUTH_PATTERNS = (
    r"\b401\b",
    r"unauthorized",
    r"sign.?in",
    r"cookie.*(invalid|expired)",
)
_VSD_TRANSIENT_PATTERNS = (
    r"connection reset",
    r"connection refused",
    r"timed out",
    r"timeout",
    r"temporarily unavailable",
    r"\b5\d\d\b",
    r"stream.*(error|closed)",
    r"error sending request",
    r"unexpected eof",
    r"broken pipe",
)


def _matches(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _has_challenge_markers(headers: dict | None, body: str | None) -> bool:
    normalized = {str(k).lower(): str(v).lower() for k, v in (headers or {}).items()}

    if normalized.get("cf-mitigated", "").startswith("challenge"):
        return True

    if "cloudflare" in normalized.get("server", "") and "cf-ray" in normalized:
        return True

    text = (body or "").lower()
    return any(marker in text for marker in CHALLENGE_BODY_MARKERS)


def _looks_like_auth_failure(final_url: str | None, body: str | None) -> bool:
    url = (final_url or "").lower()

    if any(marker in url for marker in AUTH_URL_MARKERS):
        return True

    text = (body or "").lower()
    return any(marker in text for marker in AUTH_BODY_MARKERS)


def classify_playwright_response(
    status: int | None,
    headers: dict | None = None,
    body: str | None = None,
    final_url: str | None = None,
    *,
    block_detection_enabled: bool = True,
) -> Detection | None:
    """
    Classify a Playwright navigation response.

    :return Detection | None: None when the response is a success.
    """
    if status is None:
        return Detection.RETRYABLE_TRANSIENT

    if status < 400:
        return None

    if status == 429:
        if block_detection_enabled:
            return Detection.RETRYABLE_THROTTLE
        return Detection.RETRYABLE_TRANSIENT

    if status in (408, 500, 502, 503, 504):
        return Detection.RETRYABLE_TRANSIENT

    if status in (401, 403):
        if block_detection_enabled and _has_challenge_markers(headers, body):
            return Detection.RETRYABLE_THROTTLE

        if _looks_like_auth_failure(final_url, body):
            return Detection.AUTH_FAILURE

        if status == 401:
            return Detection.AUTH_FAILURE

        if not block_detection_enabled:
            return Detection.RETRYABLE_TRANSIENT

        return Detection.FATAL

    return Detection.FATAL


def classify_vsd_error(
    returncode: int,
    stderr: str | None,
    *,
    block_detection_enabled: bool = True,
) -> Detection | None:
    """
    Classify a vsd subprocess failure from its exit code and stderr.

    :return Detection | None: None when the process succeeded.
    """
    if returncode == 0:
        return None

    text = (stderr or "").lower()

    if block_detection_enabled:
        if _matches(_VSD_THROTTLE_PATTERNS, text):
            return Detection.RETRYABLE_THROTTLE

        if "403" in text and _matches(_VSD_CHALLENGE_PATTERNS, text):
            return Detection.RETRYABLE_THROTTLE

        if _matches(_VSD_AUTH_PATTERNS, text):
            return Detection.AUTH_FAILURE

        if _matches(_VSD_TRANSIENT_PATTERNS, text):
            return Detection.RETRYABLE_TRANSIENT

        return Detection.FATAL

    if _matches(_VSD_AUTH_PATTERNS, text):
        return Detection.AUTH_FAILURE

    if _matches(_VSD_TRANSIENT_PATTERNS, text):
        return Detection.RETRYABLE_TRANSIENT

    if "429" in text or "403" in text:
        return Detection.RETRYABLE_TRANSIENT

    return Detection.FATAL


def parse_retry_after(value: str | None, *, clock: Callable[[], float] = time.time):
    """Parse a Retry-After header value into seconds, or None if unusable."""
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        seconds = float(text)
    except ValueError:
        seconds = None

    if seconds is not None:
        return max(0.0, seconds)

    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None

    if parsed is None:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return max(0.0, parsed.timestamp() - clock())


async def sleep_with_jitter(
    delay: float,
    jitter: float,
    *,
    sleep: Sleep = asyncio.sleep,
    rng: random.Random = _RNG,
):
    """Sleep for delay plus uniform jitter in [0, jitter]."""
    if delay <= 0 and jitter <= 0:
        return

    wait = delay

    if jitter > 0:
        wait += rng.uniform(0, jitter)

    await sleep(wait)


def _compute_wait(
    policy: RetryPolicy,
    retry_number: int,
    retry_after: float | None,
    rng: random.Random,
) -> tuple[float, bool]:
    """Return the wait for a retry and whether a Retry-After was capped."""
    if retry_after is not None:
        if retry_after > policy.retry_after_max:
            logger.warning(
                f"Retry-After {retry_after:.0f}s exceeds cap "
                f"{policy.retry_after_max:.0f}s; waiting "
                f"{policy.retry_after_max:.0f}s"
            )
            return policy.retry_after_max, True

        return retry_after, False

    computed = min(policy.max_delay, policy.base_delay * 2 ** (retry_number - 1))

    if policy.jitter:
        return rng.uniform(0, computed), False

    return computed, False


async def run_with_retry(
    op: Callable[[], Awaitable],
    policy: RetryPolicy,
    stats: ThrottleStats,
    *,
    label: str,
    sleep: Sleep = asyncio.sleep,
    rng: random.Random = _RNG,
):
    """
    Run an operation, retrying classified failures with exponential backoff.

    :param Callable op: Async operation to run.
    :param RetryPolicy policy: Retry/backoff policy.
    :param ThrottleStats stats: Run-level counters to update.
    :param str label: Human-readable operation label for logs.
    :raises LoginError: On a classified authentication failure.
    :raises RetryExhaustedError: When retries are exhausted.
    """

    total_attempts = 1 + (policy.max_retries if policy.enabled else 0)

    for attempt in range(1, total_attempts + 1):
        try:
            return await op()

        except RetrySignal as failure:
            if failure.detection is Detection.AUTH_FAILURE:
                raise LoginError(failure.reason or "Authentication required")

            if failure.detection is Detection.FATAL:
                raise

            if failure.detection is Detection.RETRYABLE_THROTTLE:
                stats.throttles += 1

            if attempt >= total_attempts:
                stats.exhausted += 1
                raise RetryExhaustedError(
                    label=label, attempts=attempt, reason=failure.reason
                )

            wait, capped = _compute_wait(policy, attempt, failure.retry_after, rng)

            if capped:
                stats.cap_hits += 1

            stats.retries += 1
            stats.waits += 1
            logger.warning(
                f"Retry {label}: attempt {attempt + 1}/{total_attempts} "
                f"after {wait:.2f}s ({failure.reason})"
            )
            await sleep(wait)
