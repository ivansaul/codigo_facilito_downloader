"""
Expanders utilities for Facilito API
"""

import re

from playwright.sync_api import Page

from ..errors import CourseError


def expand_course_sections(page: Page) -> None:
    """Expand all sections in the course by simulating a click on each section's header.

    This function searches for all <form> elements with a class matching 'reveal-form-NNNN'
    and an action attribute formatted as '/blocks/NNNN.json'. It then extracts the value
    of the action attribute to execute a script that expands the section.

    Example:
    <form
        class="reveal-form-1371" action="/blocks/1371.json" accept-charset="UTF-8"
        data-remote="true" method="get"><input name="utf8" type="hidden" value="✓">
    </form>

    Args:
        page (Page): The playwright page object representing the web page.

    Raises:
        FacilitoCourseSectionNotExpandedError: If the action value is not found or the
                                        block container is not found for any course section.
    """

    sections = page.query_selector_all("form[data-remote='true'][method='get']")

    for section in sections:
        # get action value -> /blocks/NNNN.json
        action_value = section.get_attribute("action")

        if action_value is None:
            raise CourseError("Action value not found")

        # get block container match -> match(NNNN)
        match_block_container = re.search(r"\d+", action_value)

        if match_block_container is None:
            raise CourseError("Block container not found")

        # get block container value -> NNNN
        block_container = match_block_container.group()

        script = f"""
        document.querySelector(".block-container-{block_container} .collapsible-header").click();
        """

        page.evaluate(script)
