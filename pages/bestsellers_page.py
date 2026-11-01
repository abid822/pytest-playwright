import re

from playwright.sync_api import Page, expect

from locators.bestsellers_locators import BestSellersLocators
from pages.base_page import BasePage

# Departments that stay on the Best Sellers list. The carousel below them rotates.
CORE_DEPARTMENTS = [
    "Books",
    "Electronics",
    "Home & Kitchen",
    "Toys & Games",
]


class BestSellersPage(BasePage):
    """Amazon Best Sellers: department list, then a ranked department page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.banner = page.locator(BestSellersLocators.BANNER)
        self.department_column = page.locator(BestSellersLocators.DEPARTMENT_COLUMN)
        self.ranked_items = page.locator(BestSellersLocators.RANKED_ITEM)

    def open_best_sellers(self) -> None:
        # Step 1: Open the Best Sellers landing page
        self.open(BestSellersLocators.URL)
        # Step 2: Banner is the Best Sellers page, not a bot checkpoint
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"bestsellers", re.I))
        expect(self.banner).to_be_visible()
        expect(self.banner).to_contain_text(re.compile(r"Best Sellers", re.I))

    def _department_link(self, name: str):
        # Left-column link only. The top nav has its own Toys & Games link.
        return self.department_column.get_by_role(
            "link", name=re.compile(rf"^{re.escape(name)}$", re.I)
        ).first

    def expect_core_departments(self, names: list[str] | None = None) -> None:
        # Step 1: The department column is on screen
        expect(self.department_column).to_be_visible()
        # Step 2: Each core department is listed
        missing = []
        for name in names or CORE_DEPARTMENTS:
            link = self._department_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Best Sellers departments: {missing}"

    def open_department(self, name: str) -> None:
        # Step 1: Open that department from the left column
        link = self._department_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        link.scroll_into_view_if_needed()
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        try:
            expect(self.page).to_have_url(re.compile(r"/zgbs/"), timeout=8000)
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, f"{name} department link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"/zgbs/"))
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(rf"Best Sellers in {re.escape(name)}", re.I),
            )
        ).to_be_visible()

    def expect_number_one_product(self) -> None:
        # The department list ranks products, and #1 has a title.
        expect(self.ranked_items.first).to_be_visible()
        first = self.ranked_items.first
        expect(first.locator(BestSellersLocators.RANK_BADGE).first).to_have_text(
            re.compile(r"#\s*1")
        )
        title = first.locator(BestSellersLocators.PRODUCT_LINK).filter(
            has_text=re.compile(r"[A-Za-z]")
        )
        expect(title.first).to_be_visible()
        text = " ".join((title.first.inner_text() or "").split())
        assert text, "Number one Best Seller has no product title"
