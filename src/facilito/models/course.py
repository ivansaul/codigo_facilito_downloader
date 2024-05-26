""" Course model """

from typing import Optional

from pydantic import BaseModel


class VideoURL(BaseModel):
    """Video model, video of URL"""

    id: Optional[str] = None
    title: str
    url: str


class CourseSection(BaseModel):
    """course section model"""

    id: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    videos_url: list[VideoURL]


class Course(BaseModel):
    """Course model"""

    id: Optional[str] = None
    url: str
    title: str
    description: Optional[str] = None
    sections: list[CourseSection]
