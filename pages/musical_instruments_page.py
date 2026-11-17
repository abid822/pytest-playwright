import re

from playwright.sync_api import Page, expect

from locators.musical_instruments_locators import MusicalInstrumentsLocators
from pages.base_page import BasePage

# Departments that stay in the Musical Instruments strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Guitars",
    "Bass",
    "Keyboards",
    "Amplifiers & Effects",
]


class MusicalInstrumentsPage(BasePage):
    """Amazon Musical Instruments: store categories, then a priced amplifier."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(MusicalInstrumentsLocators.SUBNAV)

    def _musical_instruments_ready(self) -> bool:
        # The store has no page heading. The title and the strip identify it.
        try:
            title = self.page.title() or ""
            if not re.search(r"Musical Instruments", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_musical_instruments(self) -> None:
        # Step 1: Open the Musical Instruments store.
        # The first response is sometimes a shell with no strip.
        self.open(MusicalInstrumentsLocators.URL)
        for _ in range(2):
            if self._musical_instruments_ready():
                break
            self.page.goto(
                MusicalInstrumentsLocators.URL, wait_until="domcontentloaded"
            )
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Musical Instruments store is showing, not a bot checkpoint.
        # The document title says "Musical Instruments".
        expect(self.page).to_have_url(re.compile(r"node=11091801"))
        expect(self.page).to_have_title(re.compile(r"Musical Instruments", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(MusicalInstrumentsLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Musical Instruments categories: {missing}"
