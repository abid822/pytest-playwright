import re

from playwright.sync_api import Page, expect

from locators.haul_locators import HaulLocators
from pages.base_page import BasePage

# Departments that stay in the Haul strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Women",
    "Men",
    "Kids",
    "Home",
]


class HaulPage(BasePage):
    """Amazon Haul: store categories, then a priced women's item."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(HaulLocators.SUBNAV)
        self.results = page.locator(HaulLocators.RESULTS)

    def _haul_ready(self) -> bool:
        # The store title and the strip identify it.
        try:
            title = self.page.title() or ""
            if not re.search(r"Amazon Haul", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_haul(self) -> None:
        # Step 1: Open the Amazon Haul store.
        # The first response is sometimes a shell with no strip.
        self.open(HaulLocators.URL)
        for _ in range(2):
            if self._haul_ready():
                break
            self.page.goto(HaulLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: Amazon Haul is showing, not a bot checkpoint.
        expect(self.page).to_have_url(re.compile(r"/haul/store"))
        self.expect_title(re.compile(r"Amazon Haul", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Match the whole label. "Home" must not also match "Home Improvement",
        # and "Men" must not also match "Women". A trailing symbol (the Deals
        # bolt) is still that label.
        return self.page.locator(HaulLocators.SUBNAV_LINK).filter(
            has_text=re.compile(
                rf"^\s*{re.escape(name)}(?:\s*[^\w\s]+)?\s*$", re.I
            )
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
        assert not missing, f"Missing Haul categories: {missing}"

    def open_category(self, name: str) -> None:
        # Step 1: Open that category from the store strip
        link = self._category_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        assert "i=bazaar" in href, f"{name} category link is not a Haul search"
        link.click()
        # Step 2: If the click does not open the Haul search, follow the href
        pattern = re.compile(r"[?&]i=bazaar(?:&|$)")
        try:
            expect(self.page).to_have_url(pattern, timeout=8000)
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, f"{name} category link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        if not pattern.search(self.page.url or ""):
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(pattern)
        expect(self.page).to_have_url(
            re.compile(rf"[?&](?:k|field-keywords)=[^&]*{re.escape(name)}", re.I)
        )
        self.expect_title(re.compile(r"Amazon Haul", re.I))
        self.expect_title(re.compile(re.escape(name), re.I))
        expect(self.results.first).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(HaulLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), f"Haul product has no price: {text!r}"
