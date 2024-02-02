"""
Constants
"""

from enum import Enum

COOKIES_FILE = ".cookies.txt"
BASE_URL = "https://codigofacilito.com"
LOGIN_URL = "https://codigofacilito.com/users/sign_in"
SAMPLE_VIDEO_URL = "https://codigofacilito.com/videos/icon"
SAMPLE_ARTICLE_URL = ""  # TODO: find article url
SAMPLE_COURSE_URL = "https://codigofacilito.com/cursos/flutter-profesional"
VIDEO_URL_REGEX = r"https://codigofacilito\.com/(videos|articulos)/.+"
COURSE_URL_REGEX = r"https://codigofacilito\.com/cursos/.+"
FFMPEG_URL = "https://ffmpeg.org/download.html"
CONFIG_FILE = ".conf.json"
DOWNLOADS_DIR = "downloads"


class FileType(Enum):
    """File type"""

    PDF = "pdf"
    HTML = "html"
