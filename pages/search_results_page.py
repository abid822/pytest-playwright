import re

from playwright.sync_api import Page, expect

from locators.amazon_locators import AmazonSearchLocators
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.results = page.locator(AmazonSearchLocators.PRODUCT_CARDS)

    def add_first_result_to_cart(self) -> None:
        expect(self.results.first).to_be_visible()
        add_on_card = self.results.first.get_by_role(
            "button", name=re.compile(r"Add to cart", re.I)
        )
        if add_on_card.count() > 0:
            add_on_card.first.click()
            return

        self.results.first.locator("h2 a").first.click()
        pdp_add = self.page.locator("#add-to-cart-button")
        expect(pdp_add).to_be_visible()
        pdp_add.click()
