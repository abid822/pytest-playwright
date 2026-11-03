import re

from playwright.sync_api import Page, expect

from locators.deals_locators import DealsLocators
from pages.base_page import BasePage

# Filters that stay on Today's Deals. Seasonal bubbles come and go.
CORE_FILTERS = [
    ("Lightning deals", "deals-collection-lightning-deals"),
    ("Electronics", "electronics"),
    ("Home", "home"),
    ("Books", "books"),
]


class DealsPage(BasePage):
    """Amazon Today's Deals: filter bubbles and priced deal cards."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.cards = page.locator(DealsLocators.PRODUCT_CARD)

    def open_deals(self) -> None:
        # Step 1: Open Today's Deals
        self.open(DealsLocators.URL)
        # Step 2: The deals page is showing, not a bot checkpoint
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"/deals", re.I))
        expect(self.page).to_have_title(re.compile(r"Today's Deals", re.I))

    def _bubble(self, suffix: str):
        # Desktop uses filter-bubble-*. Mobile web uses bubble-*.
        return self.page.locator(DealsLocators.FILTER_BUBBLE.format(suffix=suffix)).first

    def expect_core_filters(self, filters: list[tuple[str, str]] | None = None) -> None:
        # Each core filter bubble is on the page.
        missing = []
        for name, suffix in filters or CORE_FILTERS:
            if self._bubble(suffix).count() == 0:
                missing.append(name)
        assert not missing, f"Missing Today's Deals filters: {missing}"

    def open_filter(self, name: str, suffix: str) -> None:
        # Step 1: Choose that filter from the bubble row
        bubble = self._bubble(suffix)
        expect(bubble).to_be_attached()
        bubble.scroll_into_view_if_needed()
        expect(bubble).to_be_visible()
        expect(bubble).to_be_enabled()
        expect(bubble).to_have_accessible_name(re.compile(rf"^{re.escape(name)}$", re.I))
        bubble.click()
        # Step 2: The deals URL records the filter and the bubble is selected
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(
            re.compile(rf"[?&]bubble-id={re.escape(suffix)}(?:&|$)")
        )
        expect(self._bubble(suffix)).to_have_attribute("aria-pressed", "true")

    def _product_title(self, card) -> str:
        # The discount badge is also a product-card link. Prefer the title.
        links = card.locator(DealsLocators.PRODUCT_LINK)
        fallback = ""
        for i in range(min(links.count(), 6)):
            text = " ".join((links.nth(i).inner_text() or "").split())
            if len(text) > len(fallback):
                fallback = text
            if re.search(r"%\s*off|\bdeal\b", text, re.I):
                continue
            if re.search(r"[A-Za-z]{3}", text):
                return text
        return fallback

    def expect_priced_deal_cards(self) -> None:
        # The grid lists products, and the first card has a title plus a price or discount.
        expect(self.cards.first).to_be_visible()
        assert self.cards.count() >= 2, "Today's Deals listed fewer than two products"
        card = self.cards.first
        title = self._product_title(card)
        assert title, "Deal card has no product title"
        text = " ".join((card.inner_text() or "").split())
        assert re.search(r"\$\s*\d|%\s*off", text, re.I), (
            f"Deal card has no price or discount: {text[:180]}"
        )
