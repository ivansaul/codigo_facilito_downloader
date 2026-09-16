import asyncio
import logging
import random
from email.utils import formatdate
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer
from pydantic import ValidationError
from typer.testing import CliRunner

from facilito import cli, config, constants
from facilito.errors import (
    AbortError,
    BaseError,
    LoginError,
    RateLimitError,
    RetryExhaustedError,
)
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
