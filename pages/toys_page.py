import re

from playwright.sync_api import Page, expect

from locators.toys_locators import ToysLocators
from pages.base_page import BasePage

# Departments that stay in the Toys & Games strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Toys & Games",
    "Shop Toys by Character",
    "Shop Best Selling Toys",
    "Shop Newly Released Toys",
]

# The Character store title says "Character Store", not the strip label.
_TITLE_PATTERNS = {
    "Shop Toys by Character": re.compile(r"Character Store", re.I),
}

# The Character store heading is shorter than the strip label.
_HEADING_PATTERNS = {
    "Shop Toys by Character": re.compile(r"Shop by Character", re.I),
}


class ToysPage(BasePage):
    """Amazon Toys & Games: store categories, then a priced character toy."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(ToysLocators.SUBNAV)

    def _toys_ready(self) -> bool:
        # The store title says Toys & Games. The strip identifies the department.
        try:
            title = self.page.title() or ""
            if not re.search(r"Toys & Games", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_toys(self) -> None:
        # Step 1: Open the Toys & Games store.
        # The first response is sometimes a shell with no strip.
        self.open(ToysLocators.URL)
        for _ in range(2):
            if self._toys_ready():
                break
            self.page.goto(ToysLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Toys & Games store is showing, not a bot checkpoint.
        # The document title says "Toys & Games".
        expect(self.page).to_have_url(re.compile(r"node=165793011"))
        self.expect_title(re.compile(r"Toys & Games", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(ToysLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Toys & Games categories: {missing}"

    def _title_pattern(self, name: str):
        return _TITLE_PATTERNS.get(name, re.compile(re.escape(name), re.I))

    def _category_heading(self, name: str):
        pattern = _HEADING_PATTERNS.get(name, re.compile(rf"^{re.escape(name)}$", re.I))
        return self.page.get_by_role("heading", name=pattern)

    def _category_ready(self, name: str) -> bool:
        try:
            title = self.page.title() or ""
            if self._title_pattern(name).search(title):
                return True
            heading = self._category_heading(name)
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
        # The click sometimes lands on a shell: right node, empty title, no prices.
        # A reload paints the category page. A second goto of the same href does not.
        if not self._category_ready(name):
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(rf"node={node}(?:&|$)"))
        self.expect_title(self._title_pattern(name))
        heading = self._category_heading(name)
        if heading.count() > 0:
            expect(heading.first).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(ToysLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Toys & Games product has no price: {text!r}"
        )
