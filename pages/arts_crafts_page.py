import re

from playwright.sync_api import Page, expect

from locators.arts_crafts_locators import ArtsCraftsLocators
from pages.base_page import BasePage

# Departments that stay in the Arts, Crafts & Sewing strip. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Fabric",
    "Art Supplies",
    "Scrapbooking",
    "Knitting & Crochet",
]


class ArtsCraftsPage(BasePage):
    """Amazon Arts, Crafts & Sewing: store categories, then a priced fabric."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(ArtsCraftsLocators.SUBNAV)

    def _arts_crafts_ready(self) -> bool:
        # The store has no page heading. The title and the strip identify it.
        try:
            title = self.page.title() or ""
            if not re.search(r"Arts, Crafts & Sewing", title, re.I):
                return False
            return self.subnav.count() > 0 and self.subnav.is_visible()
        except Exception:
            return False

    def open_arts_crafts(self) -> None:
        # Step 1: Open the Arts, Crafts & Sewing store.
        # The first response is sometimes a shell with no strip.
        self.open(ArtsCraftsLocators.URL)
        if not self._arts_crafts_ready():
            self.page.goto(ArtsCraftsLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Arts, Crafts & Sewing store is showing, not a bot checkpoint.
        # The document title says "Arts, Crafts & Sewing".
        expect(self.page).to_have_url(re.compile(r"node=2617941011"))
        expect(self.page).to_have_title(re.compile(r"Arts, Crafts & Sewing", re.I))
        expect(self.subnav).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(ArtsCraftsLocators.SUBNAV_LINK).filter(
            has_text=re.compile(re.escape(name), re.I)
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
        assert not missing, f"Missing Arts, Crafts & Sewing categories: {missing}"

    def _category_heading(self, name: str):
        return self.page.get_by_role(
            "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
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
        expect(self.page).to_have_title(re.compile(re.escape(name), re.I))
        expect(self._category_heading(name).first).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(ArtsCraftsLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Arts, Crafts & Sewing product has no price: {text!r}"
        )
