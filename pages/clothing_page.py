import re

from playwright.sync_api import Page, expect

from locators.clothing_locators import ClothingLocators
from pages.base_page import BasePage

# Departments that stay in the Clothing strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Women",
    "Men",
    "Kids",
    "Luggage",
]


class ClothingPage(BasePage):
    """Amazon Clothing, Shoes & Jewelry: store categories, then a priced bag."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(ClothingLocators.SUBNAV)

    def _clothing_ready(self) -> bool:
        # The store title says Clothing. The strip identifies the department.
        try:
            title = self.page.title() or ""
            if not re.search(r"Clothing", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_clothing(self) -> None:
        # Step 1: Open the Clothing, Shoes & Jewelry store.
        # The first response is sometimes a shell with no strip.
        self.open(ClothingLocators.URL)
        for _ in range(2):
            if self._clothing_ready():
                break
            self.page.goto(ClothingLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Clothing store is showing, not a bot checkpoint.
        # The document title says "Clothing".
        expect(self.page).to_have_url(re.compile(r"node=7141123011"))
        self.expect_title(re.compile(r"Clothing", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(ClothingLocators.SUBNAV_LINK).filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
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
        assert not missing, f"Missing Clothing categories: {missing}"

    def _category_heading(self, name: str):
        # The page heading can be longer than the strip label.
        # Luggage is the heading "Luggage & Travel Gear".
        return self.page.get_by_role(
            "heading", name=re.compile(re.escape(name), re.I)
        )

    def _category_ready(self, name: str) -> bool:
        heading = self._category_heading(name)
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_category(self, name: str) -> None:
        # Step 1: Open that category from the store strip
        link = self._category_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        match = re.search(r"node=(\d+)", href)
        assert match, f"{name} category link has no node"
        node = match.group(1)
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        try:
            expect(self.page).to_have_url(
                re.compile(rf"node={node}(?:&|$)"), timeout=8000
            )
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, f"{name} category link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # The first category response is sometimes a shell with no heading.
        if not self._category_ready(name):
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(rf"node={node}(?:&|$)"))
        self.expect_title(re.compile(re.escape(name), re.I))
        expect(self._category_heading(name).first).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(ClothingLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Clothing product has no price: {text!r}"
        )
