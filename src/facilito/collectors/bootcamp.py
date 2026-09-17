import asyncio

from playwright.async_api import BrowserContext, Page

from ..constants import BASE_URL
from ..errors import AbortError, CourseError, UnitError
from ..helpers import slugify
from ..models import Bootcamp, Module, Unit
from ..ratelimit import RateLimitSettings, ThrottleStats, throttled_goto
from ..utils import acquire_page, get_unit_type


async def _fetch_bootcamp_modules(
    page: Page,
    settings: RateLimitSettings | None = None,
    stats: ThrottleStats | None = None,
) -> list[Module]:
    """
    Fetch all modules from a bootcamp page.

    Bootcamp structure:
    - Each module is collapsible section (Módulo 1, Módulo 2, etc.)
    - Each module contains multiple classes/units
    - Units can be videos, lectures, or quizzes
    """
    # Updated selectors for bootcamp structure
    MODULES_SELECTOR = "ul.collapsible.f-topics li.f-radius-small"

    try:
        modules_selectors = page.locator(MODULES_SELECTOR)
        modules_count = await modules_selectors.count()

        if not modules_count:
            raise CourseError("No modules found in bootcamp")

        # Expand all modules to access their content
        for i in range(modules_count):
            CHEVRON_SELECTOR = ".collapsible-header"
            try:
                chevron = modules_selectors.nth(i).locator(CHEVRON_SELECTOR).first
                # Check if module is already expanded
                is_active = await modules_selectors.nth(i).get_attribute("class")
                if is_active and "active" not in is_active:
                    await chevron.click()
            except Exception:
                # Some modules might already be expanded or not clickable
                pass

        # Wait for content to load
        await asyncio.sleep(2)

        modules: list[Module] = []
        for i in range(modules_count):
            # Module name is in the header with class "f-green-text--2"
            MODULE_NAME_SELECTOR = ".collapsible-header span.f-green-text"
            UNITS_SELECTOR = ".collapsible-body ul a"

            # Get module name
            module_name_elem = (
                modules_selectors.nth(i).locator(MODULE_NAME_SELECTOR).first
            )
            module_name = await module_name_elem.text_content()

            if not module_name:
                # Try alternative selector
                MODULE_NAME_ALT_SELECTOR = ".collapsible-header h4"
                module_name = (
                    await modules_selectors.nth(i)
                    .locator(MODULE_NAME_ALT_SELECTOR)
                    .first.text_content()
                )
                if not module_name:
                    raise CourseError(
                        f"Could not extract module name for module {i + 1}"
                    )

            # Clean module name: remove newlines, extra spaces, and tabs
            module_name = " ".join(module_name.strip().split())

            # Get all units in this module
            units_locators = modules_selectors.nth(i).locator(UNITS_SELECTOR)
            units_count = await units_locators.count()

            if not units_count:
                # Module might be empty, skip it
                continue

            units: list[Unit] = []
            for j in range(units_count):
                # Unit name is in nested p tags with class "ibm"
                UNIT_NAME_SELECTOR = "p.ibm.f-text-16"

                unit_name = (
                    await units_locators.nth(j)
                    .locator(UNIT_NAME_SELECTOR)
                    .first.text_content()
                )
                unit_url = await units_locators.nth(j).first.get_attribute("href")

                if not unit_name or not unit_url:
                    # Skip invalid units
                    continue

                # Clean unit name: remove newlines, extra spaces, and tabs
                unit_name = " ".join(unit_name.strip().split())

                # Build full URL
                full_url = BASE_URL + unit_url

                # For bootcamp lessons, we need to follow the redirect
                # to get the actual video URL
                # The URLs like /cursos/bootcamp-...?play=true redirect
                # to /videos/...
                # We'll detect the type after getting the final URL
                try:
                    # Reuse one probe page so the window is not reopened per unit
                    temp_page = await acquire_page(page.context, slot="probe")
                    await throttled_goto(
                        temp_page,
                        full_url,
                        settings or RateLimitSettings(),
                        stats=stats or ThrottleStats(),
                        wait_until="domcontentloaded",
                    )
                    # Get final URL after redirects
                    final_url = temp_page.url

                    # Now determine the type based on final URL
                    unit_type = get_unit_type(final_url)

                    units.append(
                        Unit(
                            type=unit_type,
                            name=unit_name,
                            slug=slugify(unit_name),
                            url=final_url,
                        )
                    )
                except AbortError:
                    raise
                except Exception:
                    # If redirect fails, skip this unit
                    continue

            if units:  # Only add module if it has valid units
                modules.append(
                    Module(
                        name=module_name,
                        slug=slugify(module_name),
                        units=units,
                    )
                )

    except AbortError:
        raise
    except Exception as e:
        raise UnitError(f"Error fetching bootcamp modules: {str(e)}")

    return modules


async def fetch_bootcamp(
    context: BrowserContext,
    url: str,
    settings: RateLimitSettings | None = None,
    stats: ThrottleStats | None = None,
) -> Bootcamp:
    """
    Fetch all information from a bootcamp.

    Args:
        context: Playwright browser context
        url: URL of the bootcamp (e.g., https://codigofacilito.com/programas/ingles-conversacional)

    Returns:
        Bootcamp model with all modules and units

    Raises:
        CourseError: If bootcamp information cannot be extracted
    """
    # Selector for bootcamp title (similar to course)
    NAME_SELECTOR = ".f-course-presentation h1, .cover-with-image h1, h1.h1"

    try:
        page = await acquire_page(context)
        await throttled_goto(
            page,
            url,
            settings or RateLimitSettings(),
            stats=stats or ThrottleStats(),
        )

        # Wait for page to load
        await asyncio.sleep(1)

        # Get bootcamp name
        name = await page.locator(NAME_SELECTOR).first.text_content()

        if not name:
            raise CourseError("Could not extract bootcamp name")

        # Clean bootcamp name: remove newlines, extra spaces, and tabs
        name = " ".join(name.strip().split())

        # Fetch all modules
        modules = await _fetch_bootcamp_modules(page, settings, stats)

        if not modules:
            raise CourseError("No modules found in bootcamp")

    except AbortError:
        raise
    except Exception as e:
        raise CourseError(f"Error fetching bootcamp: {str(e)}")

    return Bootcamp(
        name=name,
        slug=slugify(name),
        url=url,
        modules=modules,
    )
