from facilito.models import Video, VideoProvider


def test_video_provider_defaults_to_hls():
    assert Video(url="https://x/hls/a.m3u8").provider == VideoProvider.HLS


def test_video_provider_accepts_youtube():
    video = Video(url="https://www.youtube.com/watch?v=abc", provider="youtube")

    assert video.provider == VideoProvider.YOUTUBE
