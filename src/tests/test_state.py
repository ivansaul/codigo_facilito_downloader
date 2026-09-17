import asyncio

import pytest

from facilito import state
from facilito.downloaders import bootcamp as bootcamp_downloader
from facilito.downloaders import course as course_downloader
from facilito.downloaders import unit as unit_downloader
from facilito.downloaders import video as video_downloader
from facilito.downloaders import youtube as youtube_downloader
from facilito.errors import RetryExhaustedError
from facilito.models import (
    Bootcamp,
    Chapter,
    Course,
    Module,
    TypeUnit,
    Unit,
    UnitOutcome,
    Video,
    VideoProvider,
)
from facilito.ratelimit import RateLimitSettings, ThrottleStats
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


def test_download_video_skip_returns_success(tmp_path):
    path = tmp_path / "a.mp4"
    path.write_text("v")

    outcome = asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8",
            path,
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )

    assert outcome.success is True
    assert outcome.provider == "hls"


def test_download_video_missing_vsd_returns_failure(monkeypatch, tmp_path):
    async def fake_download_vsd():
        return None

    monkeypatch.setattr(video_downloader, "_download_vsd", fake_download_vsd)

    outcome = asyncio.run(
        video_downloader.download_video.__wrapped__(
            "https://x/hls/a.m3u8",
            tmp_path / "a.mp4",
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )

    assert outcome.success is False
    assert "vsd" in outcome.error


def test_download_youtube_skip_returns_success(tmp_path):
    path = tmp_path / "v.mp4"
    path.write_text("v")

    outcome = asyncio.run(
        youtube_downloader.download_youtube.__wrapped__(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            path,
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )

    assert outcome.success is True
    assert outcome.provider == "youtube"


class _CookiesContext:
    async def cookies(self):
        return []


def test_download_unit_returns_youtube_outcome(monkeypatch, tmp_path):
    async def fake_fetch_video(context, url, settings=None, stats=None):
        return Video(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            provider=VideoProvider.YOUTUBE,
        )

    async def fake_download_youtube(url, path=None, **kwargs):
        return UnitOutcome(success=False, error="boom", provider="youtube")

    monkeypatch.setattr(unit_downloader, "fetch_video", fake_fetch_video)
    monkeypatch.setattr(unit_downloader, "download_youtube", fake_download_youtube)

    unit = Unit(type=TypeUnit.VIDEO, name="a", slug="a", url="https://x/videos/a")

    outcome = asyncio.run(
        unit_downloader.download_unit(_CookiesContext(), unit, tmp_path / "a.mp4")
    )

    assert outcome.success is False
    assert outcome.provider == "youtube"


def test_download_unit_returns_hls_outcome(monkeypatch, tmp_path):
    async def fake_fetch_video(context, url, settings=None, stats=None):
        return Video(url="https://x/hls/a.m3u8")

    async def fake_download_video(url, path=None, **kwargs):
        return UnitOutcome(success=True, provider="hls")

    monkeypatch.setattr(unit_downloader, "fetch_video", fake_fetch_video)
    monkeypatch.setattr(unit_downloader, "download_video", fake_download_video)

    unit = Unit(type=TypeUnit.VIDEO, name="a", slug="a", url="https://x/videos/a")

    outcome = asyncio.run(
        unit_downloader.download_unit(_CookiesContext(), unit, tmp_path / "a.mp4")
    )

    assert outcome.success is True
    assert outcome.provider == "hls"


def _course():
    return Course(
        name="c",
        slug="c",
        url="https://x/cursos/c",
        chapters=[
            Chapter(
                name="ch",
                slug="ch",
                units=[
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v",
                        slug="v",
                        url="https://x/videos/v",
                    )
                ],
            )
        ],
    )


def test_download_course_skips_ok_units(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    monkeypatch.setattr(course_downloader, "DIR_PATH", tmp_path)

    calls = []

    async def fake_download_unit(*args, **kwargs):
        calls.append(args)
        return UnitOutcome(success=True)

    async def fake_save_page(*args, **kwargs):
        return None

    monkeypatch.setattr(course_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(course_downloader, "save_page", fake_save_page)

    course = _course()
    unit = course.chapters[0].units[0]

    chapter_dir = tmp_path / "c" / "01_ch"
    chapter_dir.mkdir(parents=True)
    output = chapter_dir / "01_v.mp4"
    output.write_text("v")

    run = RunState(url=course.url, kind="course", slug="c")
    run.record(output.as_posix(), unit, UnitOutcome(success=True))

    asyncio.run(
        course_downloader.download_course(
            None, course, state=run, settings=RateLimitSettings()
        )
    )

    assert calls == []


def test_download_course_records_outcome(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    monkeypatch.setattr(course_downloader, "DIR_PATH", tmp_path)

    async def fake_download_unit(*args, **kwargs):
        return UnitOutcome(success=False, error="boom")

    async def fake_save_page(*args, **kwargs):
        return None

    monkeypatch.setattr(course_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(course_downloader, "save_page", fake_save_page)

    run = RunState(url="https://x/cursos/c", kind="course", slug="c")

    asyncio.run(
        course_downloader.download_course(
            None, _course(), state=run, settings=RateLimitSettings()
        )
    )

    loaded = load_state("c")
    assert loaded is not None
    assert loaded.failures()[0].error == "boom"


def test_download_course_abort_records_and_saves(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    monkeypatch.setattr(course_downloader, "DIR_PATH", tmp_path)

    async def fake_download_unit(*args, **kwargs):
        raise RetryExhaustedError("unit", 2, "HTTP 429")

    async def fake_save_page(*args, **kwargs):
        return None

    monkeypatch.setattr(course_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(course_downloader, "save_page", fake_save_page)

    run = RunState(url="https://x/cursos/c", kind="course", slug="c")

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            course_downloader.download_course(
                None, _course(), state=run, settings=RateLimitSettings()
            )
        )

    loaded = load_state("c")
    assert loaded is not None
    assert loaded.failures()[0].error is not None


def test_download_bootcamp_skips_ok_units(monkeypatch, tmp_path):
    monkeypatch.setattr(state, "APP_DIR", tmp_path)
    monkeypatch.setattr(bootcamp_downloader, "DIR_PATH", tmp_path)

    calls = []

    async def fake_download_unit(*args, **kwargs):
        calls.append(args)
        return UnitOutcome(success=True)

    async def fake_save_page(*args, **kwargs):
        return None

    monkeypatch.setattr(bootcamp_downloader, "download_unit", fake_download_unit)
    monkeypatch.setattr(bootcamp_downloader, "save_page", fake_save_page)

    bootcamp = Bootcamp(
        name="b",
        slug="b",
        url="https://x/programas/b",
        modules=[
            Module(
                name="m",
                slug="m",
                units=[
                    Unit(
                        type=TypeUnit.VIDEO,
                        name="v",
                        slug="v",
                        url="https://x/videos/v",
                    )
                ],
            )
        ],
    )
    unit = bootcamp.modules[0].units[0]

    module_dir = tmp_path / "b" / "01_m"
    module_dir.mkdir(parents=True)
    output = module_dir / "01_v.mp4"
    output.write_text("v")

    run = RunState(url=bootcamp.url, kind="bootcamp", slug="b")
    run.record(output.as_posix(), unit, UnitOutcome(success=True))

    asyncio.run(
        bootcamp_downloader.download_bootcamp(
            None, bootcamp, state=run, settings=RateLimitSettings()
        )
    )

    assert calls == []
