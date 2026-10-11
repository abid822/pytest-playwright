import re

from playwright.sync_api import Page, expect

from locators.amazon_locators import AmazonSearchLocators
from locators.amazon_tabs_locator import AmazonTabsLocator
from pages.base_page import BasePage

CORE_TABS = [
    "Best Sellers",
    "Today's Deals",
    "Prime",
    "Sell",
]


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.locator(AmazonSearchLocators.SEARCH_INPUT)
        self.search_button = page.locator(AmazonSearchLocators.SEARCH_BUTTON)
        self.nav_container = page.locator(AmazonTabsLocator.NAV_CONTAINER)
        self.tab_links = page.locator(AmazonTabsLocator.ALL_TABS_LINKS)
        self.hamburger = page.locator(AmazonTabsLocator.HAMBURGER_MENU)
        self.menu_items = page.locator(AmazonTabsLocator.MENU_ITEMS)
        self.cart_count = page.locator("#nav-cart-count")

    def open_home(self) -> None:
        self.open()
        expect(self.search_input).to_be_visible()

    def search(self, query: str) -> None:
        expect(self.search_input).to_be_visible()
        self.search_input.fill(query)
        self.search_button.click()
        expect(self.page).to_have_url(re.compile(r"k=", re.I))

    def expect_nav_container(self) -> None:
        expect(self.nav_container).to_be_visible()
        expect(self.tab_links.first).to_be_visible()

    def expect_core_tabs(self, names: list[str] | None = None) -> None:
        self.expect_nav_container()
        missing = []
        for name in names or CORE_TABS:
            tab = self.nav_container.get_by_role("link", name=re.compile(name, re.I))
            if tab.count() == 0:
                missing.append(name)
        assert not missing, f"Missing nav tabs: {missing}"

    def open_hamburger_menu(self) -> None:
        expect(self.hamburger).to_be_visible()
        self.hamburger.click()
        expect(self.menu_items.first).to_be_visible()

    def menu_item_texts(self) -> list[str]:
        texts = []
        for i in range(self.menu_items.count()):
            text = self.menu_items.nth(i).inner_text().strip()
            if text:
                texts.append(text)
        return texts

    def expect_menu_contains(self, expected: list[str]) -> None:
        actual = self.menu_item_texts()
        missing = [item for item in expected if item not in actual]
        assert not missing, f"Missing hamburger items: {missing}"

    def expect_cart_not_empty(self) -> None:
        expect(self.cart_count).not_to_have_text(re.compile(r"^0$"))
