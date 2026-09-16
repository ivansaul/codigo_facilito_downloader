from playwright.async_api import BrowserContext

from ..errors import AbortError, UnitError
from ..helpers import slugify
from ..models import TypeUnit, Unit
from ..ratelimit import RateLimitSettings, ThrottleStats, throttled_goto
from ..utils import get_unit_type


async def fetch_unit(
    context: BrowserContext,
    url: str,
    settings: RateLimitSettings | None = None,
    stats: ThrottleStats | None = None,
):
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
        await throttled_goto(
            page,
            url,
            settings or RateLimitSettings(),
            stats=stats or ThrottleStats(),
        )

        name = await page.locator(NAME_SELECTOR).first.text_content()

        if not name:
            raise UnitError()

        type = get_unit_type(url)

    except AbortError:
        raise
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
