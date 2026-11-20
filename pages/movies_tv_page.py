import re

from playwright.sync_api import Page, expect

from locators.movies_tv_locators import MoviesTvLocators
from pages.base_page import BasePage

# Departments that stay in the Movies & TV strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Movies",
    "TV shows",
    "Blu-ray",
    "4K Store",
]


class MoviesTvPage(BasePage):
    """Amazon Movies & TV: store categories, then a priced Blu-ray."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(MoviesTvLocators.SUBNAV)

    def _movies_tv_ready(self) -> bool:
        # The store title says Movies & TV. The strip identifies the department.
        try:
            title = self.page.title() or ""
            if not re.search(r"Movies & TV", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_movies_tv(self) -> None:
        # Step 1: Open the Movies & TV store.
        # The first response is sometimes a shell with no strip.
        self.open(MoviesTvLocators.URL)
        for _ in range(2):
            if self._movies_tv_ready():
                break
            self.page.goto(MoviesTvLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Movies & TV store is showing, not a bot checkpoint.
        # The document title says "Movies & TV".
        expect(self.page).to_have_url(re.compile(r"node=2625373011"))
        self.expect_title(re.compile(r"Movies & TV", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(MoviesTvLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Movies & TV categories: {missing}"
