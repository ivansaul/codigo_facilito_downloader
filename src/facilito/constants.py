import tempfile
from pathlib import Path

APP_NAME = "Facilito"
APP_DIR = Path(APP_NAME)
CONFIG_FILE = APP_DIR / "config.json"
CONFIG_ENV_VAR = "FACILITO_CONFIG"

BROWSER_ENV_VAR = "FACILITO_BROWSER"
BROWSER_CHANNELS = ("chrome", "msedge")
BROWSER_CHOICES = ("auto", *BROWSER_CHANNELS, "chromium")

SESSION_DIR = Path(tempfile.gettempdir()) / APP_NAME
SESSION_FILE = SESSION_DIR / "state.json"

BASE_URL = "https://codigofacilito.com"
LOGIN_URL = BASE_URL + "/users/sign_in"
HOME_URL = BASE_URL + "/home"

VIDEO_BASE_URL = "https://video-storage.codigofacilito.com"
VIDEO_M3U8_URL = (
    VIDEO_BASE_URL + "/hls" + "/{course_id}" + "/{video_id}" + "/playlist.m3u8"
)

# --- Session directory ---
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
