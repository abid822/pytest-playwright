import re

from playwright.sync_api import Page, expect

from locators.renewed_locators import RenewedLocators
from pages.base_page import BasePage

# Sections that stay on the Renewed store. Category tiles rotate.
CORE_SECTIONS = [
    "Explore popular brands",
    "The Renewed promise",
]


class RenewedPage(BasePage):
    """Amazon Renewed: store sections, then a priced refurbished product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.product_titles = page.locator(RenewedLocators.PRODUCT_TITLE)

    def _renewed_ready(self) -> bool:
        # The store title says Amazon Renewed, and the guarantee line has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Amazon Renewed", title, re.I):
                return False
            guarantee = self.page.get_by_text(
                re.compile(r"Amazon Renewed Guarantee", re.I)
            )
            return guarantee.count() > 0 and guarantee.first.is_visible()
        except Exception:
            return False

    def open_renewed(self) -> None:
        # Step 1: Open the Amazon Renewed store.
        # The first response is sometimes a shell with no banner.
        self.open(RenewedLocators.URL)
        for _ in range(2):
            if self._renewed_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Renewed store is showing, not a bot checkpoint.
        expect(self.page).to_have_url(re.compile(r"node=12653393011"))
        self.expect_title(re.compile(r"Amazon Renewed", re.I))
        guarantee = self.page.get_by_text(re.compile(r"Amazon Renewed Guarantee", re.I))
        expect(guarantee.first).to_be_visible()

    def expect_core_sections(self, names: list[str] | None = None) -> None:
        # Each store section is listed. Tile names under them change between visits.
        missing = []
        for name in names or CORE_SECTIONS:
            section = self.page.get_by_text(
                re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
            )
            try:
                visible = section.count() > 0 and section.first.is_visible()
            except Exception:
                visible = False
            if not visible:
                missing.append(name)
        assert not missing, f"Missing Amazon Renewed sections: {missing}"

    def expect_priced_product(self) -> None:
        # A refurbished card shows a dollar price.
        titles = self.product_titles.filter(
            has_text=re.compile(r"Renewed|Refurbished", re.I)
        )
        expect(titles.first).to_be_visible()
        for index in range(min(titles.count(), 6)):
            title = titles.nth(index)
            card = title.locator(
                "xpath=ancestor::div[.//span[contains(@class,'a-offscreen')]][1]"
            )
            price = card.locator(RenewedLocators.PRODUCT_PRICE).first
            if price.count() == 0:
                continue
            name = " ".join((title.inner_text() or "").split())
            text = " ".join((price.text_content() or "").split())
            assert re.search(r"Renewed|Refurbished", name, re.I), (
                f"Amazon Renewed product is not refurbished: {name!r}"
            )
            assert re.search(r"\$\s*\d", text), (
                f"Amazon Renewed product has no price: {text!r}"
            )
            return
        raise AssertionError("Amazon Renewed product has no price")
