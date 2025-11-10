from enum import Enum

from pydantic import BaseModel


class Quality(str, Enum):
    MAX = "max"
    P1080 = "1080p"
    P720 = "720p"
    P480 = "480p"
    P360 = "360p"
    MIN = "min"


class TypeUnit(str, Enum):
    LECTURE = "lecture"
    VIDEO = "video"
    QUIZ = "quiz"


class Resource(BaseModel):
    name: str
    url: str


class Video(BaseModel):
    id: int | None = None
    url: str
    resources: list[Resource] | None = None


class Lecture(BaseModel):
    id: int | None = None
    resources: list[Resource] | None = None


class Unit(BaseModel):
    id: int | None = None
    type: TypeUnit
    name: str
    slug: str
    url: str


class Chapter(BaseModel):
    id: int | None = None
    name: str
    slug: str
    units: list[Unit]
    description: str | None = None


class Course(BaseModel):
    id: int | None = None
    name: str
    slug: str
    url: str
    chapters: list[Chapter]
    description: str | None = None


class Module(BaseModel):
    id: int | None = None
    name: str
    slug: str
    units: list[Unit]
    description: str | None = None


class Bootcamp(BaseModel):
    id: int | None = None
    name: str
    slug: str
    url: str
    modules: list[Module]
    description: str | None = None
