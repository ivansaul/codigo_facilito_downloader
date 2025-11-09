from pathlib import Path

from playwright.async_api import BrowserContext

from ..constants import APP_NAME
from ..models import Bootcamp, TypeUnit
from ..utils import save_page
from .unit import download_unit

DIR_PATH = Path(APP_NAME)


async def download_bootcamp(context: BrowserContext, bootcamp: Bootcamp, **kwargs):
    """
    Download a Bootcamp with all its modules and units.

    :param BrowserContext context: Playwright context.
    :param Bootcamp bootcamp: Bootcamp model to download.

    :param bool override: Override existing file if exists (default: False).
    :param int threads: Number of threads to use (default: 10).

    Directory structure:
        Facilito/
        └── bootcamp-name/
            ├── source.mhtml
            ├── 01_module-1/
            │   ├── 01_unit-1.mp4
            │   ├── 02_unit-2.mhtml
            │   └── ...
            ├── 02_module-2/
            │   └── ...
            └── ...
    """
    BOOTCAMP_DIR_PATH = DIR_PATH / bootcamp.slug
    BOOTCAMP_DIR_PATH.mkdir(parents=True, exist_ok=True)

    override = kwargs.get("override", False)
    source_path = BOOTCAMP_DIR_PATH / "source.mhtml"

    # Save bootcamp page as reference
    if override or not source_path.exists():
        await save_page(context, bootcamp.url, source_path)

    # Download each module
    for idx, module in enumerate(bootcamp.modules, 1):
        MODULE_DIR_PATH = BOOTCAMP_DIR_PATH / f"{idx:02d}_{module.slug}"
        MODULE_DIR_PATH.mkdir(parents=True, exist_ok=True)

        # Download each unit in the module
        for jdx, unit in enumerate(module.units, 1):
            if unit.type == TypeUnit.VIDEO:
                await download_unit(
                    context,
                    unit,
                    MODULE_DIR_PATH / f"{jdx:02d}_{unit.slug}.mp4",
                    **kwargs,
                )

            else:
                # For lectures, quizzes, etc., save as MHTML
                await download_unit(
                    context,
                    unit,
                    MODULE_DIR_PATH / f"{jdx:02d}_{unit.slug}.mhtml",
                    **kwargs,
                )
