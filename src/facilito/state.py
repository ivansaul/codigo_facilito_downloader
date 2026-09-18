import json
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel

from .constants import APP_DIR, STATE_FILE_NAME, STATE_VERSION
from .helpers import read_json
from .logger import logger
from .models import Unit, UnitOutcome


class UnitStatus(str, Enum):
    OK = "ok"
    FAILED = "failed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_url(url: str) -> str:
    """Normalize a URL so manifests can be matched reliably."""
    parts = urlsplit(url if "://" in url else f"https://{url}")
    return f"{parts.scheme.lower()}://{parts.netloc.lower()}{parts.path.rstrip('/')}"


class UnitState(BaseModel):
    url: str
    path: str
    unit_type: str
    provider: str
    status: UnitStatus
    error: str | None = None
    updated_at: str = ""


class RunState(BaseModel):
    version: int = STATE_VERSION
    url: str
    kind: str
    slug: str
    units: dict[str, UnitState] = {}

    def is_ok(self, path: str) -> bool:
        entry = self.units.get(path)
        return entry is not None and entry.status is UnitStatus.OK

    def failures(self) -> list[UnitState]:
        return [
            unit for unit in self.units.values() if unit.status is UnitStatus.FAILED
        ]

    def completed(self) -> bool:
        return bool(self.units) and all(
            unit.status is UnitStatus.OK for unit in self.units.values()
        )

    def outputs_present(self) -> bool:
        return all(
            Path(unit.path).exists()
            for unit in self.units.values()
            if unit.status is UnitStatus.OK
        )

    def record(self, key: str, unit: Unit, outcome: UnitOutcome) -> None:
        self.units[key] = UnitState(
            url=unit.url,
            path=key,
            unit_type=unit.type.value,
            provider=outcome.provider,
            status=UnitStatus.OK if outcome.success else UnitStatus.FAILED,
            error=outcome.error,
            updated_at=_now(),
        )


def state_path(slug: str) -> Path:
    return APP_DIR / slug / STATE_FILE_NAME


def load_state(slug: str) -> RunState | None:
    path = state_path(slug)

    if not path.exists():
        return None

    try:
        return RunState.model_validate(read_json(path))
    except Exception as error:
        logger.warning(f"Could not read run state {path}: {error}")
        return None


def save_state(state: RunState) -> None:
    path = state_path(state.slug)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(path.name + ".tmp")
    data = json.dumps(state.model_dump(mode="json"), ensure_ascii=False, indent=2)

    temporary.write_text(data, encoding="utf-8")
    os.replace(temporary, path)


def find_state(url: str, root: Path | None = None) -> RunState | None:
    root = root or APP_DIR
    target = normalize_url(url)

    if not root.exists():
        return None

    for manifest in sorted(root.glob(f"*/{STATE_FILE_NAME}")):
        try:
            state = RunState.model_validate(read_json(manifest))
        except Exception:
            continue

        if normalize_url(state.url) == target:
            return state

    return None
