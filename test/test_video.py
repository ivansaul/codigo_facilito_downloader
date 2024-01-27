"""Test video"""


def test_video(sync_api, video_fixture) -> None:
    """Test video"""
    video = sync_api.video(video_fixture.url)
    assert video.id == video_fixture.id
    assert video.url == video_fixture.url
    assert video.title == video_fixture.title
    assert video.m3u8_url == video_fixture.m3u8_url
    assert video.media_type == video_fixture.media_type
