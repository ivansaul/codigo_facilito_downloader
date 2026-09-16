from facilito.helpers import extract_youtube_id
from facilito.models import Video, VideoProvider
from facilito.ratelimit import Detection, classify_youtube_error


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
