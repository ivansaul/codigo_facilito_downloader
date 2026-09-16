from pathlib import Path

from playwright.async_api import BrowserContext

from ..constants import APP_NAME
from ..models import Course, TypeUnit
from ..ratelimit import Pacer, RateLimitSettings
from ..utils import save_page
from .unit import download_unit

DIR_PATH = Path(APP_NAME)


async def download_course(context: BrowserContext, course: Course, **kwargs):
    """
    Download a Course.

    :param BrowserContext context: Playwright context.
    :param Course course: Course model to download.

    :param bool override: Override existing file if exists (default: False).
    :param int threads: Number of threads to use (default: 10).
    """
    COURSE_DIR_PATH = DIR_PATH / course.slug
    COURSE_DIR_PATH.mkdir(parents=True, exist_ok=True)

    override = kwargs.get("override", False)
    settings = kwargs.get("settings") or RateLimitSettings()
    stats = kwargs.get("stats")
    pacer = Pacer(settings)

    source_path = COURSE_DIR_PATH / "source.mhtml"

    if override or not source_path.exists():
        await save_page(
            context, course.url, source_path, settings=settings, stats=stats
        )

    for idx, chapter in enumerate(course.chapters, 1):
        CHAPTER_DIR_PATH = COURSE_DIR_PATH / f"{idx:02d}_{chapter.slug}"
        CHAPTER_DIR_PATH.mkdir(parents=True, exist_ok=True)

        for jdx, unit in enumerate(chapter.units, 1):
            if unit.type == TypeUnit.VIDEO:
                unit_path = CHAPTER_DIR_PATH / f"{jdx:02d}_{unit.slug}.mp4"
            else:
                unit_path = CHAPTER_DIR_PATH / f"{jdx:02d}_{unit.slug}.mhtml"

            skipped = (
                unit.type == TypeUnit.VIDEO and not override and unit_path.exists()
            )

            if not skipped:
                await pacer.wait()

            await download_unit(context, unit, unit_path, **kwargs)
