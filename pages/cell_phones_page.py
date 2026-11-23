import re

from playwright.sync_api import Page, expect

from locators.cell_phones_locators import CellPhonesLocators
from pages.base_page import BasePage

# Departments that stay in the Cell Phones strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Cell Phones",
    "Accessories",
    "Cases",
    "Wearable Technology",
]


class CellPhonesPage(BasePage):
    """Amazon Cell Phones & Accessories: store categories, then a priced phone."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(CellPhonesLocators.SUBNAV)

    def _cell_phones_ready(self) -> bool:
        # The store title says Cell Phones & Accessories. The strip identifies it.
        try:
            title = self.page.title() or ""
            if not re.search(r"Cell Phones & Accessories", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_cell_phones(self) -> None:
        # Step 1: Open the Cell Phones & Accessories store.
        # The first response is sometimes a shell with no strip.
        self.open(CellPhonesLocators.URL)
        for _ in range(2):
            if self._cell_phones_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Cell Phones store is showing, not a bot checkpoint.
        # The document title says "Cell Phones & Accessories".
        expect(self.page).to_have_url(re.compile(r"node=2335752011"))
        self.expect_title(re.compile(r"Cell Phones & Accessories", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(CellPhonesLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Cell Phones categories: {missing}"

    def _category_heading(self, name: str):
        return self.page.get_by_role(
            "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
        )

    def _category_ready(self, name: str) -> bool:
        try:
            title = self.page.title() or ""
            if re.search(re.escape(name), title, re.I):
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
        self.expect_title(re.compile(re.escape(name), re.I))
        heading = self._category_heading(name)
        if heading.count() > 0:
            expect(heading.first).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(CellPhonesLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Cell Phones product has no price: {text!r}"
        )
