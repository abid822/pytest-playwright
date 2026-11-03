import re

import pytest
from playwright.sync_api import expect

from locators.registry_locators import RegistryLocators
from pages.base_page import BasePage


class RegistryPage(BasePage):
    """Amazon Registry: landing page, then Baby Registry."""

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
