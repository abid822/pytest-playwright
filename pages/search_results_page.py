import re

from playwright.sync_api import Page, expect

from locators.amazon_locators import AmazonSearchLocators
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    """Search results: add the first product to the cart."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Each product card in the results grid
        self.results = page.locator(AmazonSearchLocators.PRODUCT_CARDS)

    def add_first_result_to_cart(self) -> None:
        # Step 1: Wait for the first product card
        expect(self.results.first).to_be_visible()
        add_on_card = self.results.first.get_by_role(
            "button", name=re.compile(r"Add to cart", re.I)
        )
        # Step 2: Prefer Add to cart on the card itself
        if add_on_card.count() > 0:
            add_on_card.first.click()
            return

        # Step 3: Otherwise open the product page and add from there
        self.results.first.locator("h2 a").first.click()
        pdp_add = self.page.locator("#add-to-cart-button")
        expect(pdp_add).to_be_visible()
        pdp_add.click()
