import re

from playwright.sync_api import Page, expect

from locators.electronics_locators import ElectronicsLocators
from pages.base_page import BasePage

# Categories that stay in the Electronics strip. Seasonal tiles below them rotate.
CORE_CATEGORIES = [
    "Cell Phones",
    "Computers",
    "TV & Video",
    "Headphones",
]


class ElectronicsPage(BasePage):
    """Amazon Electronics: store categories, then a priced Headphones product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(ElectronicsLocators.SUBNAV)

    def _electronics_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Electronics$", re.I)
        )

    def _electronics_ready(self) -> bool:
        heading = self._electronics_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_electronics(self) -> None:
        # Step 1: Open the Electronics store.
        # The first response is sometimes a shell with no heading.
        self.open(ElectronicsLocators.URL)
        if not self._electronics_ready():
            self.page.goto(ElectronicsLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Electronics store is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"node=172282"))
        expect(self.page).to_have_title(re.compile(r"Electronics", re.I))
        expect(self._electronics_heading().first).to_be_visible()
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"^Shop by Category$", re.I)
            ).first
        ).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(ElectronicsLocators.SUBNAV_LINK).filter(
            has_text=re.compile(re.escape(name), re.I)
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
        assert not missing, f"Missing Electronics categories: {missing}"
