import re

from playwright.sync_api import Page, expect

from locators.handmade_locators import HandmadeLocators
from pages.base_page import BasePage

# Departments that stay under Explore the Handmade Shop. Seasonal tiles rotate.
CORE_CATEGORIES = [
    "Home decor",
    "Jewelry",
    "Beauty & personal care",
    "Kitchen & dining",
]


class HandmadePage(BasePage):
    """Amazon Handmade: shop categories, then a priced Jewelry product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.shop_heading = page.locator(HandmadeLocators.SHOP_HEADING).filter(
            has_text=re.compile(r"^\s*Explore the Handmade Shop\s*$", re.I)
        )

    def _handmade_ready(self) -> bool:
        # The store title says Handmade, and the shop heading has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Handmade", title, re.I):
                return False
            return self.shop_heading.count() > 0 and self.shop_heading.first.is_visible()
        except Exception:
            return False

    def open_handmade(self) -> None:
        # Step 1: Open the Handmade store.
        # The first response is sometimes a shell with no shop tiles.
        self.open(HandmadeLocators.URL)
        for _ in range(2):
            if self._handmade_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Handmade store is showing, not a bot checkpoint.
        # The document title says "Handmade".
        expect(self.page).to_have_url(re.compile(r"node=120955898011(?:&|$)"))
        self.expect_title(re.compile(r"Handmade", re.I))
        expect(self.shop_heading.first).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the tile label.
        return self.page.locator(HandmadeLocators.CATEGORY_LINK).filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        ).first

    def expect_core_categories(self, names: list[str] | None = None) -> None:
        # Step 1: The shop heading is on screen
        expect(self.shop_heading.first).to_be_visible()
        # Step 2: Each core category is listed
        missing = []
        for name in names or CORE_CATEGORIES:
            link = self._category_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Handmade categories: {missing}"

    def open_category(self, name: str) -> None:
        # Step 1: Open that category from the shop tiles
        link = self._category_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        match = re.search(r"[?&]bbn=(\d+)", href)
        assert match, f"{name} category link has no department"
        node = match.group(1)
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        self.expect_url_or_follow(re.compile(rf"[?&]bbn={node}(?:&|$)"), href)
        # The results stay in Handmade.
        expect(self.page).to_have_url(re.compile(r"[?&]i=handmade(?:&|$)"))

    def expect_priced_product(self) -> None:
        # A product on the category page shows a dollar price.
        price = self.page.locator(HandmadeLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Handmade product has no price: {text!r}"
        )
