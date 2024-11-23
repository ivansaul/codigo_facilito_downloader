import tempfile
from pathlib import Path

APP_NAME = "Facilito"
SESSION_DIR = Path(tempfile.gettempdir()) / APP_NAME
SESSION_FILE = SESSION_DIR / "state.json"

BASE_URL = "https://codigofacilito.com"
LOGIN_URL = BASE_URL + "/users/sign_in"
HOME_URL = BASE_URL + "/home"

VIDEO_M3U8_URL = (
    "https://video-storage.codigofacilito.com"
    + "/hls"
    + "/{course_id}"
    + "/{video_id}"
    + "/playlist.m3u8"
)

# --- Session directory ---
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
