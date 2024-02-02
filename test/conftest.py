"""Fixtures for tests"""

import pytest
from src.api import FacilitoApi
from src.models.video import Video

##################
# VIDEO FIXTURES #
###################


@pytest.fixture(scope="session")
def video_fixture() -> Video:
    """Fixture for video"""
    return Video(
        id="11829",
        url="https://codigofacilito.com/videos/que-es-flutter-7e0ca18b-7bdf-4375-a62d-ac0aa90b41c1",
        title="¿Qué es Flutter?",
        m3u8_url="https://video-storage.codigofacilito.com/hls/364/11829/playlist.m3u8",
        media_type="streaming",
    )


################
# API FIXTURES #
################


@pytest.fixture(scope="session", name="navigation_timeout")
def navigation_timeout_fixture() -> int:
    """Fixture for navigation timeout"""
    return 30 * 1000


@pytest.fixture(scope="session", name="navigation_retries")
def navigation_retries_fixture() -> int:
    """Fixture for navigation retries"""
    return 5


@pytest.fixture(scope="session", name="headless_browsing")
def headless_browsing_fixture() -> bool:
    """Fixture for headless browsing"""
    return False


@pytest.fixture(scope="function", name="sync_api")
def sync_api(navigation_timeout, navigation_retries, headless_browsing):
    """Fixture for sync api"""
    with FacilitoApi(
        navigation_timeout=navigation_timeout,
        navigation_retries=navigation_retries,
        headless=headless_browsing,
    ) as api:
        yield api
