import re

from playwright.sync_api import Page, expect

from locators.beauty_locators import BeautyLocators
from pages.base_page import BasePage

# Categories that stay in the Beauty strip. Seasonal tiles below them rotate.
CORE_CATEGORIES = [
    "Makeup",
    "Skin Care",
    "Hair Care",
    "Fragrance",
]


class BeautyPage(BasePage):
    """Amazon Beauty: store categories, then a priced Makeup product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(BeautyLocators.SUBNAV)

    def _beauty_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Beauty & Personal Care$", re.I)
        )

    def _beauty_ready(self) -> bool:
        heading = self._beauty_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_beauty(self) -> None:
        # Step 1: Open the Beauty store.
        # The first response is sometimes a shell with no heading.
        self.open(BeautyLocators.URL)
        if not self._beauty_ready():
            self.page.goto(BeautyLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Beauty store is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"node=3760911"))
        expect(self.page).to_have_title(re.compile(r"Beauty", re.I))
        expect(self._beauty_heading().first).to_be_visible()
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"^Featured categories$", re.I)
            ).first
        ).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(BeautyLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Beauty categories: {missing}"

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
        expect(self.page).to_have_url(re.compile(rf"node={node}(?:&|$)"))
        expect(self.page).to_have_title(re.compile(re.escape(name), re.I))
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
            ).first
        ).to_be_visible()

    def expect_priced_product(self) -> None:
        # A product card on the category page shows a dollar price.
        price = self.page.locator(BeautyLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), f"Beauty product has no price: {text!r}"
