from facilito.helpers import extract_youtube_id
from facilito.models import Video, VideoProvider


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
