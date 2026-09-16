import os
from pathlib import Path
from typing import Any

import typer
from pydantic import ValidationError

from . import constants
from .helpers import read_json
from .ratelimit import RateLimitSettings


def _resolve_config_path(config_path: Path | None) -> tuple[Path, bool]:
    """Resolve the config file path and whether it was explicitly requested."""
    if config_path is not None:
        return config_path, True

    env_path = os.environ.get(constants.CONFIG_ENV_VAR)

    if env_path:
        return Path(env_path), True

    return constants.CONFIG_FILE, False


def resolve_settings(
    cli_overrides: dict[str, Any],
    config_path: Path | None = None,
) -> RateLimitSettings:
    """
    Resolve rate-limiting settings with CLI > config file > default precedence.

    :param dict[str, Any] cli_overrides: CLI values; None entries are ignored.
    :param Path | None config_path: Explicit config path, overrides env/default.
    :return RateLimitSettings: Validated settings.
    :raises typer.BadParameter: If an explicit config file is missing or invalid.
    """

    path, explicit = _resolve_config_path(config_path)
    file_values: dict[str, Any] = {}

    if path.exists():
        try:
            data = read_json(path)
        except Exception as error:
            raise typer.BadParameter(f"Could not read config file {path}: {error}")

        if not isinstance(data, dict):
            raise typer.BadParameter(f"Config file {path} must contain a JSON object")

        try:
            file_values = RateLimitSettings.model_validate(data).model_dump()
        except ValidationError as error:
            raise typer.BadParameter(f"Invalid config file {path}: {error}")

    elif explicit:
        raise typer.BadParameter(f"Config file not found: {path}")

    overrides = {
        key: value for key, value in cli_overrides.items() if value is not None
    }

    try:
        return RateLimitSettings.model_validate(
            {**RateLimitSettings().model_dump(), **file_values, **overrides}
        )

    except ValidationError as error:
        raise typer.BadParameter(str(error))
