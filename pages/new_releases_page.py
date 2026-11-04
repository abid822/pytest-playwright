import re

from playwright.sync_api import Page, expect

from locators.new_releases_locators import NewReleasesLocators
from pages.base_page import BasePage

# Departments that stay on the New Releases list. The carousel below them rotates.
CORE_DEPARTMENTS = [
    "Books",
    "Electronics",
    "Home & Kitchen",
    "Computers & Accessories",
]


class NewReleasesPage(BasePage):
    """Amazon New Releases: department list, then a ranked department page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.banner = page.locator(NewReleasesLocators.BANNER)
        self.department_column = page.locator(NewReleasesLocators.DEPARTMENT_COLUMN)
        self.ranked_items = page.locator(NewReleasesLocators.RANKED_ITEM)

    def _on_landing_page(self) -> bool:
        return bool(re.search(r"/gp/new-releases/?($|\?)", self.page.url or "", re.I))

    def open_new_releases(self) -> None:
        # Step 1: Open the New Releases landing page.
        # Continue shopping sometimes returns to the homepage, so load it once more.
        self.open(NewReleasesLocators.URL)
        if not self._on_landing_page():
            self.page.goto(NewReleasesLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: Banner is the New Releases page, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/gp/new-releases/?($|\?)", re.I))
        expect(self.banner).to_be_visible()
        expect(self.banner).to_contain_text(re.compile(r"New Releases", re.I))

    def _department_link(self, name: str):
        # Left-column link only. The top nav has its own Electronics link.
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
        assert not missing, f"Missing New Releases departments: {missing}"

    def open_department(self, name: str) -> None:
        # Step 1: Open that department from the left column
        link = self._department_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        link.scroll_into_view_if_needed()
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        try:
            expect(self.page).to_have_url(
                re.compile(r"/gp/new-releases/[^/?#]+", re.I),
                timeout=8000,
            )
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, f"{name} department link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"/gp/new-releases/[^/?#]+", re.I))
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(rf"New Releases in {re.escape(name)}", re.I),
            )
        ).to_be_visible()

    def expect_number_one_product(self) -> None:
        # The department list ranks products, and #1 has a title.
        expect(self.ranked_items.first).to_be_visible()
        first = self.ranked_items.first
        expect(first.locator(NewReleasesLocators.RANK_BADGE).first).to_have_text(
            re.compile(r"#\s*1")
        )
        title = first.locator(NewReleasesLocators.PRODUCT_LINK).filter(
            has_text=re.compile(r"[A-Za-z]")
        )
        expect(title.first).to_be_visible()
        text = " ".join((title.first.inner_text() or "").split())
        assert text, "Number one New Release has no product title"
