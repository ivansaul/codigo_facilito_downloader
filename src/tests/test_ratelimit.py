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
    RateLimitSettings,
    RetryPolicy,
    RetrySignal,
    ThrottleStats,
    parse_retry_after,
    run_with_retry,
    sleep_with_jitter,
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
