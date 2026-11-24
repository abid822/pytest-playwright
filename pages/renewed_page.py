import re

from playwright.sync_api import Page, expect

from locators.renewed_locators import RenewedLocators
from pages.base_page import BasePage

# Categories that stay on the Renewed grid. Brand tiles rotate.
CORE_CATEGORIES = [
    "Computer & Accessories",
    "Tablets",
    "Cameras",
    "Headphones",
]


class RenewedPage(BasePage):
    """Amazon Renewed: store categories, then a priced Headphones product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.category_links = page.locator(RenewedLocators.CATEGORY_LINK)

    def _renewed_ready(self) -> bool:
        # The store title says Amazon Renewed, and the guarantee line has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Amazon Renewed", title, re.I):
                return False
            guarantee = self.page.get_by_text(
                re.compile(r"Amazon Renewed Guarantee", re.I)
            )
            return guarantee.count() > 0 and guarantee.first.is_visible()
        except Exception:
            return False

    def open_renewed(self) -> None:
        # Step 1: Open the Amazon Renewed store.
        # The first response is sometimes a shell with no banner.
        self.open(RenewedLocators.URL)
        for _ in range(2):
            if self._renewed_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Renewed store is showing, not a bot checkpoint.
        expect(self.page).to_have_url(re.compile(r"node=12653393011"))
        self.expect_title(re.compile(r"Amazon Renewed", re.I))
        guarantee = self.page.get_by_text(re.compile(r"Amazon Renewed Guarantee", re.I))
        expect(guarantee.first).to_be_visible()
        self._reveal_categories()

    def _reveal_categories(self) -> None:
        # The category grid sits under the banner and is sometimes not in the DOM yet.
        for _ in range(8):
            if self._categories_present():
                return
            self.page.mouse.wheel(0, 1200)
            self.page.wait_for_timeout(400)

    def _categories_present(self) -> bool:
        return all(self._category_link(name).count() > 0 for name in CORE_CATEGORIES)

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. Match the tile label.
        return self.category_links.filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        ).first

    def expect_core_categories(self, names: list[str] | None = None) -> None:
        # Step 1: Scroll until the grid is in the document
        self._reveal_categories()
        # Step 2: Each core category is listed
        missing = []
        for name in names or CORE_CATEGORIES:
            link = self._category_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Amazon Renewed categories: {missing}"

    def _category_node(self, href: str) -> str:
        # Search links encode the department as n%3A172541 or n:172541.
        match = re.search(r"(?:n%3A|n:)(\d+)", href)
        return match.group(1) if match else ""

    def _category_ready(self, node: str) -> bool:
        try:
            url = self.page.url or ""
            if node not in url or "12653393011" not in url:
                return False
            price = self.page.locator(RenewedLocators.PRODUCT_PRICE)
            return price.count() > 0
        except Exception:
            return False

    def open_category(self, name: str) -> None:
        # Step 1: Open that category from the Renewed grid
        self._reveal_categories()
        link = self._category_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        node = self._category_node(href)
        assert node, f"{name} category link has no node"
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        pattern = re.compile(rf"(?:n%3A|n:){node}(?:&|$)")
        try:
            expect(self.page).to_have_url(pattern, timeout=8000)
        except AssertionError:
            self._open_href(href)
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # The click sometimes lands on a shell: right node, no prices.
        # A reload paints the category page. A second goto of the same href does not.
        if not self._category_ready(node):
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"srs=12653393011"))
        expect(self.page).to_have_url(pattern)
        # The document title stays "Amazon.com". The search scope names the store.
        scope = self.page.locator(RenewedLocators.SEARCH_SCOPE).first
        expect(scope).to_be_visible()
        expect(scope).to_contain_text(re.compile(r"Amazon Renewed", re.I))

    def expect_priced_product(self) -> None:
        # A result on the category page is marked Renewed and shows a dollar price.
        card = self.page.locator(RenewedLocators.RESULT_CARD).first
        title = card.locator(RenewedLocators.RESULT_TITLE).first
        expect(title).to_be_visible()
        name = " ".join((title.inner_text() or "").split())
        assert re.search(r"Renewed", name, re.I), (
            f"Amazon Renewed result is not marked Renewed: {name!r}"
        )
        price = card.locator(RenewedLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Amazon Renewed product has no price: {text!r}"
        )
