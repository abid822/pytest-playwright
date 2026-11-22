import re

from playwright.sync_api import Page, expect

from locators.audible_locators import AudibleLocators
from pages.base_page import BasePage

# Departments that stay in the Audible strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Audible Membership",
    "Audiobook Deals",
    "Now Trending",
    "Categories",
]

# The deals page title says "Audible Deals", not the strip label.
_TITLE_PATTERNS = {
    "Audiobook Deals": re.compile(r"Audible Deals", re.I),
}


class AudiblePage(BasePage):
    """Audible Books & Originals: store categories, then a priced deal."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(AudibleLocators.SUBNAV)

    def _audible_ready(self) -> bool:
        # The store title says Audible. The strip identifies the department.
        try:
            title = self.page.title() or ""
            if not re.search(r"Audible", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_audible(self) -> None:
        # Step 1: Open the Audible store.
        # The first response is sometimes a shell with no strip.
        self.open(AudibleLocators.URL)
        for _ in range(2):
            if self._audible_ready():
                break
            self.page.goto(AudibleLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Audible store is showing, not a bot checkpoint.
        # The document title says "Audible".
        expect(self.page).to_have_url(re.compile(r"node=18145289011"))
        self.expect_title(re.compile(r"Audible", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the strip label.
        return self.page.locator(AudibleLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Audible categories: {missing}"

    def _title_pattern(self, name: str):
        return _TITLE_PATTERNS.get(name, re.compile(re.escape(name), re.I))

    def _category_heading(self, name: str):
        pattern = _TITLE_PATTERNS.get(name, re.compile(rf"^{re.escape(name)}$", re.I))
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
        # An audiobook card on the deals page shows a dollar price.
        price = self.page.locator(AudibleLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Audible deal has no price: {text!r}"
        )
