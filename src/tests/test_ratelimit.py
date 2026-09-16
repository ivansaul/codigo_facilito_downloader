from pathlib import Path

import pytest
import typer
from pydantic import ValidationError

from facilito import config, constants
from facilito.errors import (
    AbortError,
    BaseError,
    LoginError,
    RateLimitError,
    RetryExhaustedError,
)
from facilito.ratelimit import RateLimitSettings


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
