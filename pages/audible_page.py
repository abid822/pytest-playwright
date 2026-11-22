import re

from playwright.sync_api import Page, expect

from locators.audible_locators import AudibleLocators
from pages.base_page import BasePage

# Labels that stay in the Audible strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Audible Membership",
    "Audiobook Deals",
    "Now Trending",
    "Categories",
]


class AudiblePage(BasePage):
    """Amazon Audible: store categories, then a priced Audiobook Deal."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(AudibleLocators.SUBNAV)

    def _audible_ready(self) -> bool:
        # The store title says Audible. The strip identifies the department.
        try:
            title = self.page.title() or ""
            if not re.search(r"Audible", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_audible(self) -> None:
        # Step 1: Open the Audible store.
        # The first response is sometimes a shell with no strip.
        self.open(AudibleLocators.URL)
        for _ in range(2):
            if self._audible_ready():
                break
            self.page.goto(AudibleLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Audible store is showing, not a bot checkpoint.
        # The document title says "Audible".
        expect(self.page).to_have_url(re.compile(r"node=18145289011"))
        self.expect_title(re.compile(r"Audible", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(AudibleLocators.SUBNAV_LINK).filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        ).first

    def expect_core_categories(self, names: list[str] | None = None) -> None:
        # Step 1: The store strip is on screen
        expect(self.subnav).to_be_visible()
        # Step 2: Each core category is listed
        missing = []
        for name in names or CORE_CATEGORIES:
            link = self._category_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Audible categories: {missing}"
