import re

import pytest
from playwright.sync_api import Page, expect

from locators.registry_locators import RegistryLocators
from pages.base_page import BasePage

# Tiles that stay on the Registry & Gifting landing page.
CORE_REGISTRIES = [
    ("Baby Registry", RegistryLocators.BABY_TILE),
    ("Wedding Registry", RegistryLocators.WEDDING_TILE),
    ("Gift List", RegistryLocators.GIFT_LIST_TILE),
]


class RegistryPage(BasePage):
    """Amazon Registry: landing tiles, then Baby Registry find-by-name."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.find_by_name_input = page.locator(RegistryLocators.FIND_BY_NAME_INPUT)
        self.find_by_name_button = page.locator(RegistryLocators.FIND_BY_NAME_BUTTON)

    def _page_unavailable(self) -> bool:
        # Amazon sometimes answers with Page Not Found or a generic error.
        title = self.page.title() or ""
        return bool(re.search(r"Page Not Found|Something went wrong", title, re.I))

    def _tile(self, name: str, selector: str):
        # Text starts after whitespace, so do not anchor the match.
        return self.page.locator(selector).filter(
            has_text=re.compile(re.escape(name), re.I)
        ).first

    def open_registry(self) -> None:
        # Step 1: Open the Registry & Gifting landing page.
        # The first response is sometimes an error page; load it once more.
        self.open(RegistryLocators.URL)
        if self._page_unavailable():
            self.page.goto(RegistryLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The registry page is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/registries/?($|\?)", re.I))
        if self._page_unavailable():
            pytest.skip("Amazon returned an error page for Registry")
        expect(self.page).to_have_title(re.compile(r"Registry", re.I))

    def open_baby_registry(self) -> None:
        # Step 1: Open Baby Registry from the landing page
        link = self._tile("Baby Registry", RegistryLocators.BABY_TILE)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        link.scroll_into_view_if_needed()
        link.click()
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # Step 2: A direct error page gets one more load of the same link
        if self._page_unavailable() and href:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        if self._page_unavailable():
            pytest.skip("Amazon returned an error page for Baby Registry")
        expect(self.page).to_have_url(re.compile(r"/baby-reg", re.I))

    def expect_core_registries(self, registries: list[tuple[str, str]] | None = None) -> None:
        # Each featured registry tile is on the landing page.
        missing = []
        for name, selector in registries or CORE_REGISTRIES:
            tile = self._tile(name, selector)
            try:
                expect(tile).to_be_visible()
            except AssertionError:
                missing.append(name)
        assert not missing, f"Missing Registry tiles: {missing}"

    def expect_find_by_name(self) -> None:
        # Baby Registry offers a name search, and the box can be typed in.
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r"Find a baby registry by name", re.I),
            )
        ).to_be_visible()
        expect(self.find_by_name_input).to_be_visible()
        expect(self.find_by_name_input).to_be_editable()
        expect(self.find_by_name_button).to_be_visible()
        expect(self.find_by_name_button).to_be_enabled()
