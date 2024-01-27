""" Video model """
from typing import Literal, Optional

import yt_dlp  # type: ignore
from pydantic import BaseModel

MediaType = Literal["streaming", "reading", None]


class Video(BaseModel):
    """Video model"""

    id: str
    url: str
    title: str
    description: Optional[str] = None
    m3u8_url: Optional[str] = None
    media_type: MediaType = None

    def download(self, **yt_dlp_params) -> None:
        """Download video"""
        with yt_dlp.YoutubeDL(params=yt_dlp_params) as ydl:
            ydl.download([self.m3u8_url])
