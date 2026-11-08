import re

from playwright.sync_api import Page, expect

from locators.cart_locators import CartLocators
from pages.base_page import BasePage


class CartPage(BasePage):
    """Shopping cart before anything has been added."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.empty_cart = page.locator(CartLocators.EMPTY_CART)
        self.empty_heading = page.locator(CartLocators.EMPTY_HEADING)
        self.deals_link = page.locator(CartLocators.DEALS_LINK)
        self.sign_in_link = page.locator(CartLocators.SIGN_IN_LINK)
        self.sign_up_link = page.locator(CartLocators.SIGN_UP_LINK)
        self.cart_count = page.locator(CartLocators.CART_COUNT)

    def _empty_ready(self) -> bool:
        heading = self.empty_heading
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_cart(self) -> None:
        # Step 1: Open the shopping cart.
        # The first response is sometimes a shell with no heading.
        self.open(CartLocators.URL)
        if not self._empty_ready():
            self.page.goto(CartLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The cart page is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/gp/cart/view\.html", re.I))
        expect(self.page).to_have_title(re.compile(r"Shopping Cart", re.I))
        expect(self.empty_cart).to_be_visible()
        expect(self.empty_heading.first).to_be_visible()

    def expect_empty(self) -> None:
        # The empty copy is showing and the header badge is still 0.
        expect(self.empty_heading.first).to_have_text(
            re.compile(r"Your Amazon Cart is empty", re.I)
        )
        expect(self.cart_count).to_be_visible()
        expect(self.cart_count).to_have_text(re.compile(r"^0$"))

    def expect_sign_in_and_deals(self) -> None:
        # A guest can sign in, create an account, or jump to Today's Deals.
        expect(self.sign_in_link).to_be_visible()
        expect(self.sign_in_link).to_have_attribute(
            "href", re.compile(r"cart_empty_sign_in")
        )
        expect(self.sign_up_link).to_be_visible()
        expect(self.sign_up_link).to_have_attribute("href", re.compile(r"/ap/register"))
        expect(self.deals_link).to_be_visible()
        expect(self.deals_link).to_have_attribute(
            "href", re.compile(r"cart_empty_deals")
        )
        expect(self.deals_link).to_have_text(re.compile(r"Shop today's deals", re.I))
