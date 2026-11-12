import re

from playwright.sync_api import Page, expect

from locators.home_locators import SearchLocators
from locators.product_locators import ProductLocators
from pages.base_page import BasePage


class ProductPage(BasePage):
    """Product detail page opened from a search result."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.results = page.locator(SearchLocators.PRODUCT_CARDS)

    def _skip_card(self, card) -> bool:
        if card.get_by_text(re.compile(r"^Sponsored$")).count() > 0:
            return True
        if card.get_by_text(re.compile(r"Currently unavailable", re.I)).count() > 0:
            return True
        return False

    def open_first_result(self) -> None:
        # Step 1: Results are on screen. A bot checkpoint skips the test.
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.results.first).to_be_visible()
        # Step 2: Open the first organic product. Sponsored cards are skipped.
        for i in range(min(self.results.count(), 12)):
            card = self.results.nth(i)
            if self._skip_card(card):
                continue
            link = card.locator(ProductLocators.RESULT_LINK).first
            if link.count() == 0:
                continue
            href = link.get_attribute("href") or ""
            link.scroll_into_view_if_needed()
            expect(link).to_be_visible()
            link.click()
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
            # Step 3: If the click does not leave search, follow the product href
            try:
                expect(self.page).to_have_url(re.compile(r"/dp/"), timeout=8000)
            except AssertionError:
                if href.startswith("/"):
                    href = "https://www.amazon.com" + href
                assert href, "Search result has no product link"
                self.page.goto(href, wait_until="domcontentloaded")
                self.wait_for_page_load()
                self.dismiss_continue_shopping()
            expect(self.page).to_have_url(re.compile(r"/dp/"))
            return
        raise AssertionError("No organic search result could be opened")

    def expect_title_price_and_add_to_cart(self) -> None:
        # The desktop buy box shows a title, a dollar price, and Add to cart.
        title = self.page.locator(ProductLocators.TITLE).first
        expect(title).to_be_visible()
        text = " ".join((title.inner_text() or "").split())
        assert len(text) > 3, f"Product title is empty: {text!r}"

        price = self.page.locator(ProductLocators.PRICE).first
        expect(price).to_be_visible()
        price_text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", price_text), (
            f"Product has no price: {price_text!r}"
        )

        add = self.page.locator(ProductLocators.ADD_TO_CART).first
        expect(add).to_be_visible()
