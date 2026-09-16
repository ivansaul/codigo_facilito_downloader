import asyncio
import sys
import types
from unittest.mock import MagicMock

import pytest

from facilito import constants
from facilito.collectors import video as video_collector
from facilito.downloaders import youtube as youtube_downloader
from facilito.downloaders.youtube import download_youtube, quality_to_format
from facilito.errors import RetryExhaustedError
from facilito.helpers import extract_youtube_id
from facilito.models import Quality, Video, VideoProvider
from facilito.ratelimit import (
    Detection,
    RateLimitSettings,
    ThrottleStats,
    classify_youtube_error,
)


def test_video_provider_defaults_to_hls():
    assert Video(url="https://x/hls/a.m3u8").provider == VideoProvider.HLS


def test_video_provider_accepts_youtube():
    video = Video(url="https://www.youtube.com/watch?v=abc", provider="youtube")

    assert video.provider == VideoProvider.YOUTUBE


def test_extract_youtube_id_variants():
    assert (
        extract_youtube_id("https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1")
        == "dQw4w9WgXcQ"
    )
    assert (
        extract_youtube_id("https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")
        == "dQw4w9WgXcQ"
    )
    assert extract_youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert (
        extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s")
        == "dQw4w9WgXcQ"
    )
    assert (
        extract_youtube_id("https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ")
        == "dQw4w9WgXcQ"
    )


def test_extract_youtube_id_invalid():
    assert extract_youtube_id("") is None
    assert extract_youtube_id("https://example.com/videos/abc") is None
    assert extract_youtube_id("https://youtu.be/short") is None


def test_classify_youtube_error_table():
    assert classify_youtube_error("HTTP Error 429") is Detection.RETRYABLE_THROTTLE
    assert classify_youtube_error("Too Many Requests") is Detection.RETRYABLE_THROTTLE

    assert classify_youtube_error("Sign in to confirm your age") is (
        Detection.AUTH_FAILURE
    )

    assert classify_youtube_error("Video unavailable") is Detection.FATAL
    assert classify_youtube_error("Private video") is Detection.FATAL
    assert classify_youtube_error("This video has been removed") is Detection.FATAL
    assert classify_youtube_error("no video formats found") is Detection.FATAL

    assert classify_youtube_error("connection reset by peer") is (
        Detection.RETRYABLE_TRANSIENT
    )
    assert classify_youtube_error("HTTP Error 503") is Detection.RETRYABLE_TRANSIENT
    assert classify_youtube_error("timed out") is Detection.RETRYABLE_TRANSIENT

    assert classify_youtube_error("something unexpected") is Detection.FATAL
    assert classify_youtube_error(None) is Detection.FATAL


def test_quality_to_format_table():
    assert quality_to_format(Quality.MAX) == "bestvideo*+bestaudio/best"
    assert quality_to_format(Quality.MIN) == "worstvideo*+worstaudio/worst"

    for quality, height in (
        (Quality.P1080, 1080),
        (Quality.P720, 720),
        (Quality.P480, 480),
        (Quality.P360, 360),
    ):
        assert f"height<={height}" in quality_to_format(quality)


def _install_fake_yt_dlp(monkeypatch, download_impl):
    module = types.ModuleType("yt_dlp")

    class FakeYoutubeDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def download(self, urls):
            download_impl(self.options, urls)

    module.YoutubeDL = FakeYoutubeDL
    monkeypatch.setitem(sys.modules, "yt_dlp", module)

    return module


URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_download_youtube_success(monkeypatch, tmp_path):
    path = tmp_path / "v.mp4"
    captured = {}

    def impl(options, urls):
        captured["options"] = options
        captured["urls"] = urls
        path.write_text("video")

    _install_fake_yt_dlp(monkeypatch, impl)

    asyncio.run(
        download_youtube.__wrapped__(
            URL, path, settings=RateLimitSettings(), stats=ThrottleStats()
        )
    )

    assert path.read_text() == "video"
    assert captured["urls"] == [URL]
    assert captured["options"]["noplaylist"] is True
    assert captured["options"]["format"] == "bestvideo*+bestaudio/best"


def test_download_youtube_skips_existing(monkeypatch, tmp_path):
    path = tmp_path / "v.mp4"
    path.write_text("done")

    def impl(options, urls):
        raise AssertionError("should not download an existing file")

    _install_fake_yt_dlp(monkeypatch, impl)

    asyncio.run(
        download_youtube.__wrapped__(
            URL, path, settings=RateLimitSettings(), stats=ThrottleStats()
        )
    )


def test_download_youtube_retries_transient(monkeypatch, tmp_path):
    path = tmp_path / "v.mp4"
    calls = {"count": 0}

    def impl(options, urls):
        calls["count"] += 1

        if calls["count"] == 1:
            path.write_text("partial")
            raise Exception("connection reset by peer")

        path.write_text("video")

    _install_fake_yt_dlp(monkeypatch, impl)
    settings = RateLimitSettings(
        max_retries=2, retry_base_delay=0.1, retry_max_delay=0.1
    )
    stats = ThrottleStats()

    asyncio.run(download_youtube.__wrapped__(URL, path, settings=settings, stats=stats))

    assert calls["count"] == 2
    assert stats.retries == 1
    assert path.read_text() == "video"


def test_download_youtube_fatal_not_retried(monkeypatch, tmp_path):
    path = tmp_path / "v.mp4"
    calls = {"count": 0}

    def impl(options, urls):
        calls["count"] += 1
        raise Exception("Video unavailable")

    _install_fake_yt_dlp(monkeypatch, impl)
    mock_logger = MagicMock()
    monkeypatch.setattr(youtube_downloader, "logger", mock_logger)

    settings = RateLimitSettings(
        max_retries=3, retry_base_delay=0.1, retry_max_delay=0.1
    )

    asyncio.run(
        download_youtube.__wrapped__(
            URL, path, settings=settings, stats=ThrottleStats()
        )
    )

    assert calls["count"] == 1
    assert mock_logger.exception.called


def test_download_youtube_exhaustion_aborts(monkeypatch, tmp_path):
    path = tmp_path / "v.mp4"

    def impl(options, urls):
        raise Exception("connection reset by peer")

    _install_fake_yt_dlp(monkeypatch, impl)
    settings = RateLimitSettings(
        max_retries=1, retry_base_delay=0.1, retry_max_delay=0.1
    )

    with pytest.raises(RetryExhaustedError):
        asyncio.run(
            download_youtube.__wrapped__(
                URL, path, settings=settings, stats=ThrottleStats()
            )
        )


def test_download_youtube_missing_dependency(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "yt_dlp", None)
    mock_logger = MagicMock()
    monkeypatch.setattr(youtube_downloader, "logger", mock_logger)

    asyncio.run(
        download_youtube.__wrapped__(
            URL,
            tmp_path / "v.mp4",
            settings=RateLimitSettings(),
            stats=ThrottleStats(),
        )
    )

    assert mock_logger.error.called


class FakeResponse:
    def __init__(self, status=200, url="https://x/videos/a"):
        self.status = status
        self.headers = {}
        self.url = url


class FakeAttrLocator:
    def __init__(self, value):
        self._value = value

    @property
    def first(self):
        return self

    async def get_attribute(self, name):
        return self._value


class FakePage:
    def __init__(self, content="", iframes=None, attributes=None):
        self._content = content
        self._iframes = iframes or []
        self._attributes = attributes or {}
        self.url = "https://x/videos/a"

    def on(self, *args, **kwargs):
        return None

    async def goto(self, url, **kwargs):
        return FakeResponse(url=url)

    async def content(self):
        return self._content

    async def evaluate(self, script):
        return None

    async def eval_on_selector_all(self, selector, script):
        return self._iframes

    def locator(self, selector):
        return FakeAttrLocator(self._attributes.get(selector, ""))

    async def close(self):
        return None


class FakeContext:
    def __init__(self, page):
        self._page = page

    async def new_page(self):
        return self._page


def test_find_youtube_id_prefers_iframes():
    iframes = ["https://www.youtube.com/embed/aaaaaaaaaaa"]
    markup = "https://youtu.be/bbbbbbbbbbb"

    assert video_collector._find_youtube_id(iframes, markup) == "aaaaaaaaaaa"


def test_find_youtube_id_falls_back_to_markup():
    markup = '<iframe src="https://www.youtube-nocookie.com/embed/zzzzzzzzzzz">'

    assert video_collector._find_youtube_id([], markup) == "zzzzzzzzzzz"


def test_find_youtube_id_none():
    assert video_collector._find_youtube_id([], "<html></html>") is None


def test_fetch_video_detects_youtube_embed(monkeypatch):
    monkeypatch.setattr(video_collector, "PLAYLIST_TIMEOUT", 0)

    page = FakePage(iframes=["https://www.youtube.com/embed/dQw4w9WgXcQ"])

    result = asyncio.run(
        video_collector.fetch_video(FakeContext(page), "https://x/videos/intro")
    )

    assert result.provider == VideoProvider.YOUTUBE
    assert result.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_fetch_video_prefers_hls_over_youtube(monkeypatch):
    monkeypatch.setattr(video_collector, "PLAYLIST_TIMEOUT", 0)

    page = FakePage(
        content='<source src="/hls/1/2/playlist.m3u8">',
        iframes=["https://www.youtube.com/embed/dQw4w9WgXcQ"],
    )

    result = asyncio.run(
        video_collector.fetch_video(FakeContext(page), "https://x/videos/intro")
    )

    assert result.provider == VideoProvider.HLS
    assert result.url == f"{constants.VIDEO_BASE_URL}/hls/1/2/playlist.m3u8"
