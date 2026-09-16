import asyncio
import logging
import random
import subprocess
from email.utils import formatdate
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import typer
from pydantic import ValidationError
from typer.testing import CliRunner

from facilito import async_api, cli, config, constants, downloaders, utils
from facilito.async_api import AsyncFacilito
from facilito.collectors import bootcamp, course, unit, video
from facilito.downloaders import bootcamp as bootcamp_downloader
from facilito.downloaders import course as course_downloader
from facilito.downloaders import unit as unit_downloader
from facilito.downloaders import video as video_downloader
from facilito.errors import (
    AbortError,
    BaseError,
    LoginError,
    RateLimitError,
    RetryExhaustedError,
)
from facilito.models import Bootcamp, Chapter, Course, Module, TypeUnit, Unit
from facilito.ratelimit import (
    Detection,
    Pacer,
    RateLimitSettings,
    RetryPolicy,
    RetrySignal,
    ThrottleStats,
    classify_playwright_response,
    classify_vsd_error,
    parse_retry_after,
    redact_url,
    run_with_retry,
    sleep_with_jitter,
    throttled_goto,
)

runner = CliRunner()


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


def test_settings_defaults():
    settings = RateLimitSettings()

    assert settings.request_delay == 0.0
    assert settings.request_jitter == 0.0
    assert settings.download_delay == 0.0
    assert settings.retry_enabled is True
    assert settings.max_retries == 3
    assert settings.retry_base_delay == 1.0
    assert settings.retry_max_delay == 30.0
    assert settings.retry_after_max == 60.0
    assert settings.block_detection_enabled is True


@pytest.mark.parametrize(
    "overrides",
    [
        {"request_delay": -1.0},
        {"request_jitter": -1.0},
        {"download_delay": -1.0},
        {"max_retries": 11},
        {"max_retries": -1},
        {"retry_base_delay": 0.0},
        {"retry_max_delay": 0.0},
        {"retry_after_max": 0.0},
    ],
)
def test_settings_rejects_out_of_range(overrides):
    with pytest.raises(ValidationError):
        RateLimitSettings(**overrides)


def test_settings_rejects_max_delay_lower_than_base_delay():
    with pytest.raises(ValidationError):
        RateLimitSettings(retry_base_delay=10.0, retry_max_delay=5.0)


def test_settings_rejects_unknown_key():
    with pytest.raises(ValidationError):
        RateLimitSettings(concurrency=4)


def test_config_constants():
    assert constants.APP_DIR == Path(constants.APP_NAME)
    assert constants.CONFIG_FILE == Path("Facilito") / "config.json"
    assert constants.CONFIG_ENV_VAR == "FACILITO_CONFIG"


def test_resolve_settings_defaults_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.delenv(constants.CONFIG_ENV_VAR, raising=False)
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    assert config.resolve_settings({}) == RateLimitSettings()


def test_resolve_settings_reads_file(monkeypatch, tmp_path):
    monkeypatch.delenv(constants.CONFIG_ENV_VAR, raising=False)
    cfg = tmp_path / "config.json"
    cfg.write_text('{"request_delay": 1.5, "max_retries": 5}')

    settings = config.resolve_settings({}, config_path=cfg)

    assert settings.request_delay == 1.5
    assert settings.max_retries == 5
    assert settings.download_delay == 0.0


def test_resolve_settings_cli_wins_over_file(monkeypatch, tmp_path):
    monkeypatch.delenv(constants.CONFIG_ENV_VAR, raising=False)
    cfg = tmp_path / "config.json"
    cfg.write_text('{"request_delay": 1.5, "max_retries": 5}')

    settings = config.resolve_settings({"request_delay": 3.0}, config_path=cfg)

    assert settings.request_delay == 3.0
    assert settings.max_retries == 5


def test_resolve_settings_ignores_none_overrides(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text('{"request_delay": 2.0}')

    settings = config.resolve_settings(
        {"request_delay": None, "download_delay": None}, config_path=cfg
    )

    assert settings.request_delay == 2.0


def test_resolve_settings_honors_env_var(monkeypatch, tmp_path):
    cfg = tmp_path / "env.json"
    cfg.write_text('{"download_delay": 4.0}')
    monkeypatch.setenv(constants.CONFIG_ENV_VAR, str(cfg))

    assert config.resolve_settings({}).download_delay == 4.0


def test_resolve_settings_rejects_unknown_key_in_file(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text('{"concurrency": 4}')

    with pytest.raises(typer.BadParameter):
        config.resolve_settings({}, config_path=cfg)


def test_resolve_settings_rejects_invalid_bounds_in_file(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text('{"request_delay": -1}')

    with pytest.raises(typer.BadParameter):
        config.resolve_settings({}, config_path=cfg)


def test_resolve_settings_rejects_missing_explicit_config(tmp_path):
    with pytest.raises(typer.BadParameter):
        config.resolve_settings({}, config_path=tmp_path / "nope.json")


def test_resolve_settings_rejects_invalid_cli_override(monkeypatch, tmp_path):
    monkeypatch.delenv(constants.CONFIG_ENV_VAR, raising=False)
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    with pytest.raises(typer.BadParameter):
        config.resolve_settings({"request_delay": -1})


def test_cli_download_help_lists_rate_limit_options():
    result = runner.invoke(cli.app, ["download", "--help"], env={"COLUMNS": "200"})

    assert result.exit_code == 0

    for option in [
        "--request-delay",
        "--request-jitter",
        "--download-delay",
        "--retry",
        "--no-retry",
        "--max-retries",
        "--retry-base-delay",
        "--retry-max-delay",
        "--retry-after-max",
        "--block-detection",
        "--no-block-detection",
        "--config",
    ]:
        assert option in result.output


def test_cli_download_resolves_settings(monkeypatch, tmp_path):
    captured = {}

    async def fake_download(url, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(cli, "_download", fake_download)
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    result = runner.invoke(
        cli.app,
        [
            "download",
            "https://codigofacilito.com/videos/x",
            "--max-retries",
            "0",
            "--request-delay",
            "1.5",
        ],
    )

    assert result.exit_code == 0
    assert captured["settings"].max_retries == 0
    assert captured["settings"].request_delay == 1.5


def test_cli_download_no_retry_flag(monkeypatch, tmp_path):
    captured = {}

    async def fake_download(url, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(cli, "_download", fake_download)
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    result = runner.invoke(
        cli.app,
        ["download", "https://codigofacilito.com/videos/x", "--no-retry"],
    )

    assert result.exit_code == 0
    assert captured["settings"].retry_enabled is False


def test_cli_download_rejects_invalid_value(monkeypatch, tmp_path):
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    result = runner.invoke(
        cli.app,
        ["download", "https://codigofacilito.com/videos/x", "--request-delay=-1"],
    )

    assert result.exit_code == 2


def test_cli_download_rejects_missing_explicit_config(tmp_path):
    result = runner.invoke(
        cli.app,
        [
            "download",
            "https://codigofacilito.com/videos/x",
            "--config",
            str(tmp_path / "nope.json"),
        ],
    )

    assert result.exit_code == 2


def test_cli_download_aborts_with_exit_code_one(monkeypatch, tmp_path):
    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def download(self, url, **kwargs):
            raise RetryExhaustedError(label="01_intro.mp4", attempts=4, reason="429")

    mock_logger = MagicMock()

    monkeypatch.setattr(cli, "AsyncFacilito", lambda *args, **kwargs: FakeClient())
    monkeypatch.setattr(cli, "logger", mock_logger)
    monkeypatch.setattr(config.constants, "CONFIG_FILE", tmp_path / "missing.json")

    result = runner.invoke(cli.app, ["download", "https://codigofacilito.com/videos/x"])

    assert result.exit_code == 1
    assert mock_logger.error.called


def _record_sleep(record, error=None):
    async def _sleep(duration):
        if error is not None:
            raise error

        record.append(duration)

    return _sleep


def test_parse_retry_after_delta_seconds():
    assert parse_retry_after("120") == 120.0
    assert parse_retry_after("1.5") == 1.5
    assert parse_retry_after(" 30 ") == 30.0
    assert parse_retry_after("-5") == 0.0


def test_parse_retry_after_http_date():
    now = 1_000_000_000.0

    future = formatdate(now + 120, usegmt=True)
    assert parse_retry_after(future, clock=lambda: now) == pytest.approx(120.0, abs=1.0)

    past = formatdate(now - 120, usegmt=True)
    assert parse_retry_after(past, clock=lambda: now) == 0.0


def test_parse_retry_after_garbage():
    assert parse_retry_after(None) is None
    assert parse_retry_after("") is None
    assert parse_retry_after("not-a-date") is None


def test_sleep_with_jitter_range():
    sleeps = []
    asyncio.run(
        sleep_with_jitter(1.0, 2.0, sleep=_record_sleep(sleeps), rng=random.Random(7))
    )

    assert 1.0 <= sleeps[0] <= 3.0


def test_sleep_with_jitter_noop_when_zero():
    sleeps = []
    asyncio.run(sleep_with_jitter(0.0, 0.0, sleep=_record_sleep(sleeps)))

    assert sleeps == []


def test_run_with_retry_retries_then_succeeds():
    calls = {"count": 0}
    sleeps = []

    async def op():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RetrySignal(Detection.RETRYABLE_TRANSIENT, "boom")
        return "ok"

    policy = RetryPolicy(max_retries=3, base_delay=1.0, max_delay=30.0, jitter=False)
    stats = ThrottleStats()

    result = asyncio.run(
        run_with_retry(op, policy, stats, label="unit", sleep=_record_sleep(sleeps))
    )

    assert result == "ok"
    assert sleeps == [1.0, 2.0]
    assert stats.retries == 2
    assert stats.waits == 2
    assert stats.exhausted == 0


def test_run_with_retry_respects_max_delay():
    sleeps = []

    async def op():
        raise RetrySignal(Detection.RETRYABLE_TRANSIENT, "boom")

    policy = RetryPolicy(max_retries=3, base_delay=1.0, max_delay=2.0, jitter=False)

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            run_with_retry(
                op, policy, ThrottleStats(), label="unit", sleep=_record_sleep(sleeps)
            )
        )

    assert sleeps == [1.0, 2.0, 2.0]


def test_run_with_retry_zero_retries_single_attempt():
    sleeps = []

    async def op():
        raise RetrySignal(Detection.RETRYABLE_TRANSIENT, "boom")

    policy = RetryPolicy(max_retries=0)

    with pytest.raises(RetryExhaustedError) as excinfo:
        asyncio.run(
            run_with_retry(
                op, policy, ThrottleStats(), label="unit", sleep=_record_sleep(sleeps)
            )
        )

    assert excinfo.value.attempts == 1
    assert sleeps == []


def test_run_with_retry_disabled_single_attempt():
    sleeps = []

    async def op():
        raise RetrySignal(Detection.RETRYABLE_THROTTLE, "429")

    policy = RetryPolicy(enabled=False, max_retries=5)

    with pytest.raises(RetryExhaustedError) as excinfo:
        asyncio.run(
            run_with_retry(
                op, policy, ThrottleStats(), label="unit", sleep=_record_sleep(sleeps)
            )
        )

    assert excinfo.value.attempts == 1
    assert sleeps == []


def test_run_with_retry_exhaustion_counters():
    async def op():
        raise RetrySignal(Detection.RETRYABLE_THROTTLE, "429")

    policy = RetryPolicy(max_retries=2, base_delay=1.0, max_delay=30.0, jitter=False)
    stats = ThrottleStats()

    with pytest.raises(RetryExhaustedError) as excinfo:
        asyncio.run(
            run_with_retry(op, policy, stats, label="unit", sleep=_record_sleep([]))
        )

    assert excinfo.value.label == "unit"
    assert excinfo.value.attempts == 3
    assert stats.throttles == 3
    assert stats.retries == 2
    assert stats.exhausted == 1


def test_run_with_retry_honors_retry_after():
    calls = {"count": 0}
    sleeps = []

    async def op():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RetrySignal(Detection.RETRYABLE_THROTTLE, "429", retry_after=5.0)
        return "ok"

    policy = RetryPolicy(max_retries=3, retry_after_max=60.0)
    stats = ThrottleStats()

    asyncio.run(
        run_with_retry(op, policy, stats, label="unit", sleep=_record_sleep(sleeps))
    )

    assert sleeps == [5.0]
    assert stats.throttles == 1
    assert stats.cap_hits == 0


def test_run_with_retry_caps_retry_after(caplog):
    calls = {"count": 0}
    sleeps = []

    async def op():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RetrySignal(Detection.RETRYABLE_THROTTLE, "429", retry_after=120.0)
        return "ok"

    policy = RetryPolicy(max_retries=3, retry_after_max=60.0)
    stats = ThrottleStats()

    with caplog.at_level(logging.WARNING):
        asyncio.run(
            run_with_retry(op, policy, stats, label="unit", sleep=_record_sleep(sleeps))
        )

    assert sleeps == [60.0]
    assert stats.cap_hits == 1
    assert any("Retry-After" in record.message for record in caplog.records)


def test_run_with_retry_auth_failure_raises_login_error():
    async def op():
        raise RetrySignal(Detection.AUTH_FAILURE, "sign in required")

    policy = RetryPolicy(max_retries=3)

    with pytest.raises(LoginError):
        asyncio.run(
            run_with_retry(
                op, policy, ThrottleStats(), label="u", sleep=_record_sleep([])
            )
        )


def test_run_with_retry_fatal_is_not_retried():
    async def op():
        raise RetrySignal(Detection.FATAL, "parse error")

    with pytest.raises(RetrySignal):
        asyncio.run(
            run_with_retry(
                op,
                RetryPolicy(max_retries=3),
                ThrottleStats(),
                label="u",
                sleep=_record_sleep([]),
            )
        )


def test_run_with_retry_backoff_jitter_within_range():
    sleeps = []

    async def op():
        raise RetrySignal(Detection.RETRYABLE_TRANSIENT, "boom")

    policy = RetryPolicy(max_retries=1, base_delay=4.0, max_delay=30.0, jitter=True)

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            run_with_retry(
                op,
                policy,
                ThrottleStats(),
                label="u",
                sleep=_record_sleep(sleeps),
                rng=random.Random(1234),
            )
        )

    assert 0.0 <= sleeps[0] <= 4.0


def test_run_with_retry_propagates_cancellation():
    async def op():
        raise RetrySignal(Detection.RETRYABLE_TRANSIENT, "boom")

    sleep = _record_sleep([], error=asyncio.CancelledError())

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(
            run_with_retry(
                op, RetryPolicy(max_retries=3), ThrottleStats(), label="u", sleep=sleep
            )
        )


def test_throttle_stats_summary():
    stats = ThrottleStats(retries=2, throttles=1, waits=2, cap_hits=1, exhausted=0)

    assert ThrottleStats().has_events() is False
    assert stats.has_events() is True

    summary = stats.summary()
    assert "retries=2" in summary
    assert "throttles=1" in summary
    assert "capped=1" in summary


def test_classify_playwright_success_and_missing_status():
    assert classify_playwright_response(200, {}, None, None) is None
    assert classify_playwright_response(302, {}, None, None) is None
    assert classify_playwright_response(None) is Detection.RETRYABLE_TRANSIENT


def test_classify_playwright_throttle_and_transient():
    assert classify_playwright_response(429) is Detection.RETRYABLE_THROTTLE

    for status in (408, 500, 502, 503, 504):
        assert classify_playwright_response(status) is Detection.RETRYABLE_TRANSIENT


def test_classify_playwright_challenge_headers():
    mitigated = {"cf-mitigated": "challenge"}
    assert classify_playwright_response(403, mitigated) is Detection.RETRYABLE_THROTTLE

    cloudflare = {"Server": "cloudflare", "cf-ray": "abc123"}
    assert classify_playwright_response(403, cloudflare) is Detection.RETRYABLE_THROTTLE


def test_classify_playwright_challenge_body():
    body = "<title>Just a moment...</title>"
    assert classify_playwright_response(403, {}, body) is Detection.RETRYABLE_THROTTLE


def test_classify_playwright_auth_failure():
    login_form = '<form id="new_user"></form>'
    assert classify_playwright_response(403, {}, login_form) is Detection.AUTH_FAILURE

    sign_in_url = "https://codigofacilito.com/users/sign_in"
    assert (
        classify_playwright_response(403, {}, "", sign_in_url) is Detection.AUTH_FAILURE
    )

    assert classify_playwright_response(401) is Detection.AUTH_FAILURE


def test_classify_playwright_unknown_403_is_fatal():
    assert classify_playwright_response(403, {}, "") is Detection.FATAL


def test_classify_playwright_block_detection_disabled():
    assert (
        classify_playwright_response(429, block_detection_enabled=False)
        is Detection.RETRYABLE_TRANSIENT
    )

    mitigated = {"cf-mitigated": "challenge"}
    assert (
        classify_playwright_response(403, mitigated, block_detection_enabled=False)
        is Detection.RETRYABLE_TRANSIENT
    )


def test_classify_vsd_success_and_fatal():
    assert classify_vsd_error(0, "") is None
    assert classify_vsd_error(1, "no playlists were found in website source.\n") is (
        Detection.FATAL
    )


def test_classify_vsd_throttle():
    assert classify_vsd_error(1, "HTTP 429 Too Many Requests") is (
        Detection.RETRYABLE_THROTTLE
    )
    assert classify_vsd_error(1, "403 Forbidden: Cloudflare challenge") is (
        Detection.RETRYABLE_THROTTLE
    )
    assert classify_vsd_error(1, "retry-after: 10") is (Detection.RETRYABLE_THROTTLE)


def test_classify_vsd_transient():
    assert classify_vsd_error(1, "error sending request for url (x)") is (
        Detection.RETRYABLE_TRANSIENT
    )
    assert classify_vsd_error(1, "connection reset by peer") is (
        Detection.RETRYABLE_TRANSIENT
    )
    assert classify_vsd_error(1, "timed out") is Detection.RETRYABLE_TRANSIENT
    assert classify_vsd_error(1, "stream closed unexpectedly") is (
        Detection.RETRYABLE_TRANSIENT
    )


def test_classify_vsd_auth():
    assert classify_vsd_error(1, "401 Unauthorized") is Detection.AUTH_FAILURE
    assert classify_vsd_error(1, "please sign in") is Detection.AUTH_FAILURE


def test_classify_vsd_forbidden_is_throttle():
    assert classify_vsd_error(1, "403 Forbidden") is Detection.RETRYABLE_THROTTLE


def test_classify_vsd_block_detection_disabled():
    assert classify_vsd_error(1, "HTTP 429\n", block_detection_enabled=False) is (
        Detection.RETRYABLE_TRANSIENT
    )
    assert classify_vsd_error(1, "403 forbidden\n", block_detection_enabled=False) is (
        Detection.RETRYABLE_TRANSIENT
    )


class FakeResponse:
    def __init__(self, status, headers=None, url="https://x/videos/a"):
        self.status = status
        self.headers = headers or {}
        self.url = url


class FakePage:
    def __init__(self, responses, body=""):
        self._responses = list(responses)
        self._body = body
        self.goto_calls = 0

    async def goto(self, url, **kwargs):
        self.goto_calls += 1
        return self._responses.pop(0)

    async def content(self):
        return self._body


def test_redact_url_strips_query():
    assert redact_url("https://x/videos/a?token=secret") == "https://x/videos/a"


def test_pacer_first_operation_does_not_wait():
    settings = RateLimitSettings(download_delay=2.0, request_jitter=0.0)
    sleeps = []
    pacer = Pacer(settings, sleep=_record_sleep(sleeps))

    asyncio.run(pacer.wait())
    assert sleeps == []

    asyncio.run(pacer.wait())
    assert sleeps == [2.0]


def test_pacer_delay_with_jitter_range():
    settings = RateLimitSettings(download_delay=2.0, request_jitter=1.0)
    sleeps = []
    pacer = Pacer(settings, sleep=_record_sleep(sleeps), rng=random.Random(3))

    asyncio.run(pacer.wait())
    asyncio.run(pacer.wait())

    assert 2.0 <= sleeps[0] <= 3.0


def test_throttled_goto_success_without_pacing():
    page = FakePage([FakeResponse(200)])
    sleeps = []

    response = asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            RateLimitSettings(),
            stats=ThrottleStats(),
            sleep=_record_sleep(sleeps),
        )
    )

    assert response.status == 200
    assert page.goto_calls == 1
    assert sleeps == []


def test_throttled_goto_applies_request_pacing():
    page = FakePage([FakeResponse(200)])
    settings = RateLimitSettings(request_delay=1.0, request_jitter=1.0)
    sleeps = []

    asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            settings,
            stats=ThrottleStats(),
            sleep=_record_sleep(sleeps),
            rng=random.Random(5),
        )
    )

    assert len(sleeps) == 1
    assert 1.0 <= sleeps[0] <= 2.0


def test_throttled_goto_retries_transient_response():
    page = FakePage([FakeResponse(503), FakeResponse(200)])
    settings = RateLimitSettings(retry_base_delay=1.0, retry_max_delay=2.0)
    stats = ThrottleStats()

    response = asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            settings,
            stats=stats,
            sleep=_record_sleep([]),
        )
    )

    assert response.status == 200
    assert page.goto_calls == 2
    assert stats.retries == 1


def test_throttled_goto_honors_retry_after_cap():
    page = FakePage([FakeResponse(429, {"Retry-After": "120"}), FakeResponse(200)])
    settings = RateLimitSettings(retry_after_max=60.0)
    sleeps = []

    asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            settings,
            stats=ThrottleStats(),
            sleep=_record_sleep(sleeps),
        )
    )

    assert sleeps == [60.0]


def test_throttled_goto_retries_challenge():
    challenge = FakeResponse(403, {"cf-mitigated": "challenge"})
    page = FakePage([challenge, FakeResponse(200)])
    stats = ThrottleStats()

    response = asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            RateLimitSettings(),
            stats=stats,
            sleep=_record_sleep([]),
        )
    )

    assert response.status == 200
    assert stats.retries == 1
    assert stats.throttles == 1


def test_throttled_goto_login_failure_not_retried():
    sign_in = FakeResponse(403, {}, url="https://x/users/sign_in")
    page = FakePage([sign_in], body='<form id="new_user">')

    with pytest.raises(LoginError):
        asyncio.run(
            throttled_goto(
                page,
                "https://x/videos/a",
                RateLimitSettings(),
                stats=ThrottleStats(),
                sleep=_record_sleep([]),
            )
        )

    assert page.goto_calls == 1


def test_throttled_goto_exhaustion_raises():
    page = FakePage([FakeResponse(503), FakeResponse(503)])
    settings = RateLimitSettings(
        max_retries=1, retry_base_delay=0.1, retry_max_delay=0.1
    )

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            throttled_goto(
                page,
                "https://x/videos/a",
                settings,
                stats=ThrottleStats(),
                sleep=_record_sleep([]),
            )
        )

    assert page.goto_calls == 2


def test_throttled_goto_unknown_403_raises_signal():
    page = FakePage([FakeResponse(403)], body="")

    with pytest.raises(RetrySignal):
        asyncio.run(
            throttled_goto(
                page,
                "https://x/videos/a",
                RateLimitSettings(),
                stats=ThrottleStats(),
                sleep=_record_sleep([]),
            )
        )


def test_try_except_request_propagates_abort_error():
    @utils.try_except_request
    async def failing():
        raise RetryExhaustedError("unit", 3, "429")

    with pytest.raises(RetryExhaustedError):
        asyncio.run(failing())


def test_try_except_request_swallows_plain_exception(monkeypatch):
    monkeypatch.setattr(utils, "logger", MagicMock())

    @utils.try_except_request
    async def failing():
        raise ValueError("boom")

    assert asyncio.run(failing()) is None


def test_collector_style_handler_reraises_abort_error():
    async def collector_style():
        try:
            raise RetryExhaustedError("unit", 3, "429")
        except AbortError:
            raise
        except Exception as error:
            raise RuntimeError("converted") from error

    with pytest.raises(RetryExhaustedError):
        asyncio.run(collector_style())


class FakeCDP:
    async def send(self, method):
        return {"data": "<html></html>"}


class FakeContextPage:
    def __init__(self):
        self.context = self
        self.closed = False

    async def close(self):
        self.closed = True

    async def new_cdp_session(self, page):
        return FakeCDP()


class FakeContext:
    def __init__(self, page):
        self._page = page

    async def new_page(self):
        return self._page


def test_save_page_uses_throttled_goto(monkeypatch, tmp_path):
    calls = {}

    async def fake_goto(page, url, settings, **kwargs):
        calls["url"] = url
        calls["settings"] = settings

    async def fake_scroll(page, *args, **kwargs):
        return None

    monkeypatch.setattr(utils, "throttled_goto", fake_goto)
    monkeypatch.setattr(utils, "progressive_scroll", fake_scroll)

    page = FakeContextPage()
    path = tmp_path / "source.mhtml"
    settings = RateLimitSettings(request_delay=1.0)

    asyncio.run(
        utils.save_page(
            FakeContext(page), "https://x/cursos/a", path, settings=settings
        )
    )

    assert calls["url"] == "https://x/cursos/a"
    assert calls["settings"] is settings
    assert path.read_text(encoding="utf-8") == "<html></html>"
    assert page.closed is True


def test_save_page_defaults_settings_when_none(monkeypatch, tmp_path):
    calls = {}

    async def fake_goto(page, url, settings, **kwargs):
        calls["settings"] = settings

    async def fake_scroll(page, *args, **kwargs):
        return None

    monkeypatch.setattr(utils, "throttled_goto", fake_goto)
    monkeypatch.setattr(utils, "progressive_scroll", fake_scroll)

    asyncio.run(
        utils.save_page(
            FakeContext(FakeContextPage()),
            "https://x/cursos/a",
            tmp_path / "s.mhtml",
        )
    )

    assert isinstance(calls["settings"], RateLimitSettings)


class CollectorFakePage:
    def on(self, *args, **kwargs):
        return None

    async def close(self):
        return None


class CollectorFakeContext:
    async def new_page(self):
        return CollectorFakePage()


@pytest.mark.parametrize(
    "module,func_name,url",
    [
        (course, "fetch_course", "https://x/cursos/a"),
        (video, "fetch_video", "https://x/videos/a"),
        (unit, "fetch_unit", "https://x/videos/a"),
        (bootcamp, "fetch_bootcamp", "https://x/programas/a"),
    ],
)
def test_collectors_reraise_abort(monkeypatch, module, func_name, url):
    async def fake_goto(*args, **kwargs):
        raise RetryExhaustedError("unit", 3, "429")

    monkeypatch.setattr(module, "throttled_goto", fake_goto)

    func = getattr(module, func_name)

    with pytest.raises(RetryExhaustedError):
        asyncio.run(func(CollectorFakeContext(), url))


def test_async_download_threads_settings(monkeypatch):
    client = AsyncFacilito()
    client.authenticated = True
    client._context = object()

    captured = {}
    settings = RateLimitSettings(request_delay=1.0)

    async def fake_fetch_course(url, settings=None, stats=None):
        captured["settings"] = settings
        captured["stats"] = stats
        return SimpleNamespace(chapters=[])

    async def fake_download_course(context, course, **kwargs):
        captured["kwargs"] = kwargs

    monkeypatch.setattr(client, "fetch_course", fake_fetch_course)
    monkeypatch.setattr(downloaders, "download_course", fake_download_course)

    asyncio.run(client.download("https://x/cursos/a", settings=settings))

    assert captured["settings"] is settings
    assert isinstance(captured["stats"], ThrottleStats)
    assert captured["kwargs"]["settings"] is settings
    assert captured["kwargs"]["stats"] is captured["stats"]


def test_async_download_logs_summary_when_events(monkeypatch):
    client = AsyncFacilito()
    client.authenticated = True
    client._context = object()

    mock_logger = MagicMock()
    monkeypatch.setattr(async_api, "logger", mock_logger)

    async def fake_fetch_course(url, settings=None, stats=None):
        stats.retries += 1
        return SimpleNamespace(chapters=[])

    async def fake_download_course(context, course, **kwargs):
        return None

    monkeypatch.setattr(client, "fetch_course", fake_fetch_course)
    monkeypatch.setattr(downloaders, "download_course", fake_download_course)

    asyncio.run(client.download("https://x/cursos/a"))

    assert mock_logger.info.called


def test_async_download_no_summary_without_events(monkeypatch):
    client = AsyncFacilito()
    client.authenticated = True
    client._context = object()

    mock_logger = MagicMock()
    monkeypatch.setattr(async_api, "logger", mock_logger)

    async def fake_fetch_course(url, settings=None, stats=None):
        return SimpleNamespace(chapters=[])

    async def fake_download_course(context, course, **kwargs):
        return None

    monkeypatch.setattr(client, "fetch_course", fake_fetch_course)
    monkeypatch.setattr(downloaders, "download_course", fake_download_course)

    asyncio.run(client.download("https://x/cursos/a"))

    assert not mock_logger.info.called


def test_download_unit_forwards_settings_to_video(monkeypatch):
    captured = {}
    settings = RateLimitSettings()
    stats = ThrottleStats()

    async def fake_fetch_video(context, url, settings=None, stats=None):
        captured["fetch_settings"] = settings
        captured["fetch_stats"] = stats
        return SimpleNamespace(url="https://x/hls/a.m3u8")

    async def fake_download_video(url, path=None, **kwargs):
        captured["video_kwargs"] = kwargs

    class FakeContext:
        async def cookies(self):
            return []

    monkeypatch.setattr(unit_downloader, "fetch_video", fake_fetch_video)
    monkeypatch.setattr(unit_downloader, "download_video", fake_download_video)

    unit = Unit(type=TypeUnit.VIDEO, name="a", slug="a", url="https://x/videos/a")

    asyncio.run(
        unit_downloader.download_unit(
            FakeContext(), unit, Path("out/a.mp4"), settings=settings, stats=stats
        )
    )

    assert captured["fetch_settings"] is settings
    assert captured["fetch_stats"] is stats
    assert captured["video_kwargs"]["settings"] is settings
    assert captured["video_kwargs"]["stats"] is stats


def test_download_unit_forwards_settings_to_save_page(monkeypatch):
    captured = {}
    settings = RateLimitSettings()
    stats = ThrottleStats()

    async def fake_save_page(context, url, path, settings=None, stats=None):
        captured["settings"] = settings
        captured["stats"] = stats

    monkeypatch.setattr(unit_downloader, "save_page", fake_save_page)

    unit = Unit(type=TypeUnit.LECTURE, name="a", slug="a", url="https://x/articulos/a")

    asyncio.run(
        unit_downloader.download_unit(
            None, unit, Path("out/a.mhtml"), settings=settings, stats=stats
        )
    )

    assert captured["settings"] is settings
    assert captured["stats"] is stats


def _patch_vsd(monkeypatch, tmp_path, results, path):
    calls = {"count": 0}
    exists_seen = []

    def fake_run(command, **kwargs):
        exists_seen.append(path.exists())
        index = min(calls["count"], len(results) - 1)
        returncode, stderr = results[index]
        calls["count"] += 1
        return SimpleNamespace(returncode=returncode, stderr=stderr)

    async def fake_download_vsd():
        return tmp_path / "vsd"

    monkeypatch.setattr(video_downloader, "TMP_DIR_PATH", tmp_path)
    monkeypatch.setattr(video_downloader, "_download_vsd", fake_download_vsd)
    monkeypatch.setattr(subprocess, "run", fake_run)

    return calls, exists_seen


def test_download_video_success(monkeypatch, tmp_path):
    path = tmp_path / "a.mp4"
    calls, _ = _patch_vsd(monkeypatch, tmp_path, [(0, "")], path)

    asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8",
            path,
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )

    assert calls["count"] == 1


def test_download_video_retries_transient_and_cleans_partial(monkeypatch, tmp_path):
    path = tmp_path / "a.mp4"
    calls = {"count": 0}
    exists_seen = []

    def fake_run(command, **kwargs):
        exists_seen.append(path.exists())
        calls["count"] += 1

        if calls["count"] == 1:
            path.write_text("partial")
            return SimpleNamespace(returncode=1, stderr="connection reset")

        return SimpleNamespace(returncode=0, stderr="")

    async def fake_download_vsd():
        return tmp_path / "vsd"

    monkeypatch.setattr(video_downloader, "TMP_DIR_PATH", tmp_path)
    monkeypatch.setattr(video_downloader, "_download_vsd", fake_download_vsd)
    monkeypatch.setattr(subprocess, "run", fake_run)

    settings = RateLimitSettings(
        max_retries=2, retry_base_delay=0.1, retry_max_delay=0.1
    )

    asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8", path, settings=settings, stats=ThrottleStats()
        )
    )

    assert calls["count"] == 2
    assert exists_seen == [False, False]


def test_download_video_exhaustion_aborts(monkeypatch, tmp_path):
    path = tmp_path / "a.mp4"
    calls, _ = _patch_vsd(monkeypatch, tmp_path, [(1, "connection reset")], path)

    settings = RateLimitSettings(
        max_retries=1, retry_base_delay=0.1, retry_max_delay=0.1
    )

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            video_downloader.download_video.__wrapped__(
                "https://x/hls/a.m3u8",
                path,
                settings=settings,
                stats=ThrottleStats(),
            )
        )

    assert calls["count"] == 2


def test_download_video_auth_failure_not_retried(monkeypatch, tmp_path):
    path = tmp_path / "a.mp4"
    calls, _ = _patch_vsd(monkeypatch, tmp_path, [(1, "401 unauthorized")], path)

    mock_logger = MagicMock()
    monkeypatch.setattr(video_downloader, "logger", mock_logger)

    settings = RateLimitSettings(
        max_retries=3, retry_base_delay=0.1, retry_max_delay=0.1
    )

    asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8", path, settings=settings, stats=ThrottleStats()
        )
    )

    assert calls["count"] == 1
    assert mock_logger.exception.called


def test_download_video_skips_existing_file(monkeypatch, tmp_path):
    path = tmp_path / "a.mp4"
    path.write_text("done")

    def exploding_run(*args, **kwargs):
        raise AssertionError("vsd should not run for an existing file")

    monkeypatch.setattr(subprocess, "run", exploding_run)

    asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8",
            path,
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )


class _CountingPacer:
    def __init__(self, settings, **kwargs):
        self.settings = settings
        _CountingPacer.waits = getattr(_CountingPacer, "waits", 0)

    async def wait(self):
        _CountingPacer.waits += 1

    @classmethod
    def reset(cls):
        cls.waits = 0


def test_download_course_paces_only_real_downloads(monkeypatch, tmp_path):
    monkeypatch.setattr(course_downloader, "DIR_PATH", tmp_path)
    monkeypatch.setattr(course_downloader, "Pacer", _CountingPacer)
    _CountingPacer.reset()

    calls = []

    async def fake_download_unit(context, unit, path, **kwargs):
        calls.append(path.name)

    async def fake_save_page(context, url, path, settings=None, stats=None):
        return None

    monkeypatch.setattr(course_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(course_downloader, "save_page", fake_save_page)

    course = Course(
        name="c",
        slug="c",
        url="https://x/cursos/c",
        chapters=[
            Chapter(
                name="ch1",
                slug="ch1",
                units=[
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v1",
                        slug="v1",
                        url="https://x/videos/v1",
                    ),
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v2",
                        slug="v2",
                        url="https://x/videos/v2",
                    ),
                    Unit(
                        type=TypeUnit.LECTURE,
                        name="l1",
                        slug="l1",
                        url="https://x/articulos/l1",
                    ),
                ],
            )
        ],
    )

    chapter_dir = tmp_path / "c" / "01_ch1"
    chapter_dir.mkdir(parents=True)
    (chapter_dir / "02_v2.mp4").write_text("done")

    asyncio.run(
        course_downloader.download_course(
            None, course, settings=RateLimitSettings(download_delay=0.05)
        )
    )

    assert calls == ["01_v1.mp4", "02_v2.mp4", "03_l1.mhtml"]
    assert _CountingPacer.waits == 2


def test_download_bootcamp_paces_only_real_downloads(monkeypatch, tmp_path):
    monkeypatch.setattr(bootcamp_downloader, "DIR_PATH", tmp_path)
    monkeypatch.setattr(bootcamp_downloader, "Pacer", _CountingPacer)
    _CountingPacer.reset()

    calls = []

    async def fake_download_unit(context, unit, path, **kwargs):
        calls.append(path.name)

    async def fake_save_page(context, url, path, settings=None, stats=None):
        return None

    monkeypatch.setattr(bootcamp_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(bootcamp_downloader, "save_page", fake_save_page)

    bootcamp = Bootcamp(
        name="b",
        slug="b",
        url="https://x/programas/b",
        modules=[
            Module(
                name="m1",
                slug="m1",
                units=[
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v1",
                        slug="v1",
                        url="https://x/videos/v1",
                    ),
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v2",
                        slug="v2",
                        url="https://x/videos/v2",
                    ),
                ],
            )
        ],
    )

    module_dir = tmp_path / "b" / "01_m1"
    module_dir.mkdir(parents=True)
    (module_dir / "02_v2.mp4").write_text("done")

    asyncio.run(
        bootcamp_downloader.download_bootcamp(
            None, bootcamp, settings=RateLimitSettings(download_delay=0.05)
        )
    )

    assert calls == ["01_v1.mp4", "02_v2.mp4"]
    assert _CountingPacer.waits == 1


def test_abort_chain_propagates_end_to_end():
    page = FakePage([FakeResponse(503), FakeResponse(503)])
    settings = RateLimitSettings(
        max_retries=1, retry_base_delay=0.1, retry_max_delay=0.1
    )

    @utils.try_except_request
    async def run():
        await throttled_goto(
            page,
            "https://x/videos/a",
            settings,
            stats=ThrottleStats(),
            sleep=_record_sleep([]),
        )

    with pytest.raises(RetryExhaustedError):
        asyncio.run(run())


def test_throttled_goto_redacts_signed_urls(caplog):
    page = FakePage([FakeResponse(429, {"Retry-After": "1"}), FakeResponse(200)])
    settings = RateLimitSettings(retry_base_delay=0.1, retry_max_delay=0.1)
    signed_url = (
        "https://video-storage.codigofacilito.com/hls/519/14643/playlist.m3u8"
        "?Policy=secret&Signature=topsecret"
    )

    with caplog.at_level(logging.WARNING):
        asyncio.run(
            throttled_goto(
                page,
                signed_url,
                settings,
                stats=ThrottleStats(),
                sleep=_record_sleep([]),
            )
        )

    text = " ".join(record.message for record in caplog.records)

    assert "topsecret" not in text
    assert "Policy=secret" not in text
    assert "video-storage.codigofacilito.com/hls/519/14643/playlist.m3u8" in text


def test_defaults_add_no_waits_with_retry_enabled():
    page = FakePage([FakeResponse(200)])
    sleeps = []

    asyncio.run(
        throttled_goto(
            page,
            "https://x/videos/a",
            RateLimitSettings(),
            stats=ThrottleStats(),
            sleep=_record_sleep(sleeps),
        )
    )

    pacer = Pacer(RateLimitSettings(), sleep=_record_sleep(sleeps))
    asyncio.run(pacer.wait())
    asyncio.run(pacer.wait())

    assert sleeps == []
