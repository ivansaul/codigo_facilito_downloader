"""
Video model
"""

from enum import Enum
from typing import Optional

import yt_dlp  # type: ignore
from pydantic import BaseModel

from .. import consts, helpers
from ..utils.logger import logger
from .download import YoutubeDLLogger


class MediaType(Enum):
    """Video media type"""

    STREAMING = "streaming"
    READING = "reading"


class Quality(Enum):
    """Video quality"""

    BEST = "best"
    P1080 = "1080"
    P720 = "720"
    P480 = "480"
    P360 = "360"
    WORST = "worst"


class Video(BaseModel):
    """Video model"""

    id: str
    url: str
    title: str
    description: Optional[str]
    m3u8_url: Optional[str]
    media_type: Optional[MediaType]

    def download(
        self,
        prefix_name: str = "",
        dir_path: str = consts.DOWNLOADS_DIR,
        quality: Quality = Quality.BEST,
        cookiefile: str = consts.COOKIES_FILE,
    ) -> int:
        """video and article downloader"""

        if not self.m3u8_url:
            logger("[VIDEO] Video has no m3u8_url")
            return 0

        dlp_format = helpers.quality_to_dlp_format(quality)
        video_name = helpers.clean_string(self.title)

        # check if download dir exists
        helpers.check_dir(dir_path)

        yt_dlp_params = {
            "format": dlp_format,
            "cookiefile": cookiefile,
            "outtmpl": f"{dir_path}/{prefix_name}{video_name}.%(ext)s",
            "logger": YoutubeDLLogger(),
            "n_threads": 10,
            "retries": 5,
            # TODO: implement custom parser for progress bar
            # "progress_hooks": [YoutubeDLLogger.on_progress],
            # "quiet": True,
            # "noprogress": False,
        }

        with yt_dlp.YoutubeDL(params=yt_dlp_params) as ydl:
            status_code = ydl.download([self.m3u8_url])  # return 1 if success
            return status_code
