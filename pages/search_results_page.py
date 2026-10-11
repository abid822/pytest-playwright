import re

from playwright.sync_api import Page, expect

from locators.amazon_locators import AmazonSearchLocators
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    """Search results: sort, then add a product to the cart."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Each product card in the results grid
        self.results = page.locator(AmazonSearchLocators.PRODUCT_CARDS)
        self.sort_select = page.locator(AmazonSearchLocators.SORT_SELECT)

    def sort_by_price_low_to_high(self) -> None:
        # Step 1: Click the visible Sort by control next to the hidden native <select>
        native = self.page.locator("#s-result-sort-select")
        expect(native).to_be_attached()
        visible_sort = native.locator("xpath=following-sibling::span[contains(@class,'a-button')][1]")
        expect(visible_sort).to_be_visible()
        visible_sort.click()
        # Step 2: Choose Price: Low to High from the popover (or the native select)
        popover_option = self.page.locator(".a-popover a, a.a-dropdown-link").filter(
            has_text=re.compile(r"Price:\s*Low to High", re.I)
        )
        try:
            popover_option.first.wait_for(state="visible", timeout=4000)
            popover_option.first.click()
        except Exception:
            native.select_option("price-asc-rank")
        # Step 3: If the widget did not change the URL, follow the option's data-url
        try:
            expect(self.page).to_have_url(re.compile(r"price-asc-rank|s=price-asc"), timeout=8000)
        except AssertionError:
            href = native.locator("option[value='price-asc-rank']").get_attribute("data-url")
            assert href, "Price: Low to High option has no data-url"
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href)
            expect(self.page).to_have_url(re.compile(r"price-asc-rank|s=price-asc"))
        expect(self.results.first).to_be_visible()

    def _skip_card(self, card) -> bool:
        if card.get_by_text(re.compile(r"^Sponsored$")).count() > 0:
            return True
        if card.get_by_text(re.compile(r"Currently unavailable", re.I)).count() > 0:
            return True
        return False

    def _first_shoppable_card(self):
        # Skip Sponsored and out-of-stock tiles; lowest in-stock result is used
        expect(self.results.first).to_be_visible()
        for i in range(min(self.results.count(), 16)):
            card = self.results.nth(i)
            if not self._skip_card(card):
                return card
        return self.results.first

    def _add_from_product_page(self) -> bool:
        if self.page.get_by_text(re.compile(r"Currently unavailable", re.I)).count() > 0:
            return False
        pdp_add = self.page.locator("#add-to-cart-button").or_(
            self.page.get_by_role("button", name=re.compile(r"Add to cart", re.I))
        )
        if pdp_add.count() > 0:
            pdp_add.first.click()
            return True
        see_offers = self.page.get_by_role(
            "link", name=re.compile(r"See all buying options|See options", re.I)
        )
        if see_offers.count() == 0:
            return False
        see_offers.first.click()
        offer_add = self.page.get_by_role("button", name=re.compile(r"Add to cart", re.I))
        expect(offer_add.first).to_be_visible()
        offer_add.first.click()
        return True

    def add_first_result_to_cart(self) -> None:
        # Step 1: Walk cheapest-first results until one can be added
        expect(self.results.first).to_be_visible()
        for i in range(min(self.results.count(), 16)):
            card = self.results.nth(i)
            if self._skip_card(card):
                continue
            add_on_card = card.get_by_role(
                "button", name=re.compile(r"Add to cart", re.I)
            )
            # Step 2: Prefer Add to cart on the card itself
            if add_on_card.count() > 0:
                add_on_card.first.click()
                return
            # Step 3: Otherwise open the product page
            title = card.locator("h2 a").or_(card.locator("a[href*='/dp/']"))
            if title.count() == 0:
                continue
            title.first.click()
            if self._add_from_product_page():
                return
            self.page.go_back()
            expect(self.results.first).to_be_visible()
        raise AssertionError("No in-stock lowest-price seat cover could be added to cart")
