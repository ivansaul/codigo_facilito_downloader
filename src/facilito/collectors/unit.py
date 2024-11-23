from playwright.async_api import BrowserContext

from ..errors import UnitError
from ..helpers import slugify
from ..models import TypeUnit, Unit
from ..utils import get_unit_type


async def fetch_unit(context: BrowserContext, url: str):
    NAME_SELECTOR = ".title-section header h1"

    try:
        type = get_unit_type(url)

        if type == TypeUnit.QUIZ:
            # TODO: implement quiz fetching
            return Unit(
                type=type,
                url=url,
                name="quiz",
                slug="quiz",
            )
    except Exception:
        raise UnitError()

    try:
        page = await context.new_page()
        await page.goto(url)

        name = await page.locator(NAME_SELECTOR).first.text_content()

        if not name:
            raise UnitError()

        type = get_unit_type(url)

    except Exception:
        raise UnitError()

    finally:
        await page.close()

    return Unit(
        type=type,
        name=name,
        url=url,
        slug=slugify(name),
    )
