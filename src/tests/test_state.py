from facilito import state
from facilito.models import TypeUnit, Unit, UnitOutcome
from facilito.state import (
    RunState,
    UnitStatus,
    find_state,
    load_state,
    normalize_url,
    save_state,
    state_path,
)


def _unit(url="https://x/videos/a"):
    return Unit(type=TypeUnit.VIDEO, name="a", slug="a", url=url)


def test_unit_outcome_defaults():
    outcome = UnitOutcome(success=True)

    assert outcome.success is True
    assert outcome.error is None
    assert outcome.provider == "hls"


def test_unit_outcome_failure():
    outcome = UnitOutcome(success=False, error="HTTP 429", provider="youtube")

    assert outcome.success is False
    assert outcome.error == "HTTP 429"
    assert outcome.provider == "youtube"


def test_normalize_url():
    assert normalize_url("https://CodigoFacilito.com/cursos/go/") == (
        "https://codigofacilito.com/cursos/go"
    )
    assert normalize_url("https://x/cursos/a") == normalize_url("https://x/cursos/a/")


def test_run_state_record_and_queries(tmp_path):
    run = RunState(url="https://x/cursos/a", kind="course", slug="a")

    ok_path = (tmp_path / "a.mp4").as_posix()
    (tmp_path / "a.mp4").write_text("v")
    run.record(ok_path, _unit(), UnitOutcome(success=True))

    assert run.is_ok(ok_path) is True
    assert run.completed() is True
    assert run.outputs_present() is True
    assert run.failures() == []

    failed_path = (tmp_path / "b.mp4").as_posix()
    run.record(
        failed_path,
        _unit("https://x/videos/b"),
        UnitOutcome(success=False, error="boom"),
    )

    assert run.completed() is False
    assert len(run.failures()) == 1
    assert run.failures()[0].error == "boom"
    assert run.failures()[0].status is UnitStatus.FAILED


def test_run_state_outputs_missing(tmp_path):
    run = RunState(url="https://x/cursos/a", kind="course", slug="a")
    run.record(
        (tmp_path / "missing.mp4").as_posix(),
        _unit(),
        UnitOutcome(success=True),
    )

    assert run.completed() is True
    assert run.outputs_present() is False


def test_save_and_load_state_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)

    run = RunState(url="https://x/cursos/a", kind="course", slug="a")
    run.record(
        (tmp_path / "a" / "a.mp4").as_posix(),
        _unit(),
        UnitOutcome(success=True),
    )

    save_state(run)

    manifest = state_path("a")
    assert manifest.exists()
    assert not manifest.with_name(manifest.name + ".tmp").exists()

    loaded = load_state("a")
    assert loaded is not None
    assert loaded.url == "https://x/cursos/a"
    assert loaded.completed() is True


def test_load_state_corrupt_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    path = state_path("a")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json")

    assert load_state("a") is None


def test_load_state_missing_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)

    assert load_state("nope") is None


def test_find_state_matches_normalized_url(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)

    run = RunState(url="https://x/cursos/a", kind="course", slug="a")
    save_state(run)

    assert find_state("https://x/cursos/a/") is not None
    assert find_state("https://x/cursos/other") is None


def test_find_state_ignores_corrupt_manifests(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    path = state_path("bad")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json")

    assert find_state("https://x/cursos/a") is None


def test_find_state_without_root(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)

    assert find_state("https://x/cursos/a") is None
