import re

from playwright.sync_api import Page, expect

from locators.grocery_locators import GroceryLocators
from pages.base_page import BasePage

# Aisles that stay on the Grocery page. Seasonal tiles rotate.
CORE_AISLES = [
    "Snacks",
    "Beverages",
    "Breakfast",
    "Candy & Chocolate",
]


class GroceryPage(BasePage):
    """Amazon Grocery: store aisles, then a priced product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _grocery_heading(self):
        return self.page.get_by_role("heading", name=re.compile(r"^Grocery$", re.I))

    def _grocery_ready(self) -> bool:
        # The store heading says Grocery, and an aisle card has painted.
        try:
            heading = self._grocery_heading()
            if heading.count() == 0 or not heading.first.is_visible():
                return False
            return self.page.locator(GroceryLocators.AISLE_LINK).count() > 0
        except Exception:
            return False

    def open_grocery(self) -> None:
        # Step 1: Open the Grocery store.
        # The first response is sometimes a shell with no aisles.
        self.open(GroceryLocators.URL)
        for _ in range(2):
            if self._grocery_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Grocery store is showing, not a bot checkpoint.
        # The page heading says "Grocery".
        expect(self.page).to_have_url(re.compile(r"node=16310101(?:&|$)"))
        self.expect_title(re.compile(r"Everyday Essentials|Grocery", re.I))
        expect(self._grocery_heading().first).to_be_visible()

    def _aisle_link(self, name: str):
        # Link text includes surrounding whitespace. Match the aisle label.
        return self.page.locator(GroceryLocators.AISLE_LINK).filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        ).first

    def expect_core_aisles(self, names: list[str] | None = None) -> None:
        # Step 1: The Grocery heading is on screen
        expect(self._grocery_heading().first).to_be_visible()
        # Step 2: Each core aisle is listed
        missing = []
        for name in names or CORE_AISLES:
            link = self._aisle_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Grocery aisles: {missing}"

    def expect_breakfast_aisle(self) -> None:
        # Breakfast stays in the aisle row. The card label is the link name.
        link = self._aisle_link("Breakfast")
        expect(link).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the Grocery page shows a dollar price.
        price = self.page.locator(GroceryLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Grocery product has no price: {text!r}"
        )
