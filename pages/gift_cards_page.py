import re

from playwright.sync_api import Page, expect

from locators.gift_cards_locators import GiftCardsLocators
from pages.base_page import BasePage

# Shop-by headings that stay on the Gift Cards landing page.
SHOP_SECTIONS = [
    "Shop gift cards by occasion",
    "Shop gift cards by brand",
    "Shop gift cards by category",
    "Shop gift cards by delivery type",
]


class GiftCardsPage(BasePage):
    """Amazon Gift Cards: shop sections, then a priced Birthday eGift card."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _shop_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^The Gift Card Shop$", re.I)
        )

    def _shop_ready(self) -> bool:
        # The document title is sometimes blank. The shop heading is the check.
        heading = self._shop_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_gift_cards(self) -> None:
        # Step 1: Open the Gift Cards shop.
        # The first response is sometimes a shell with no shop heading.
        self.open(GiftCardsLocators.URL)
        if not self._shop_ready():
            self.page.goto(GiftCardsLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The shop is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/gift-cards", re.I))
        expect(self._shop_heading()).to_be_visible()

    def expect_shop_sections(self, names: list[str] | None = None) -> None:
        # Each shop-by heading is on the landing page.
        missing = []
        for name in names or SHOP_SECTIONS:
            heading = self.page.get_by_role(
                "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
            )
            if heading.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Gift Cards sections: {missing}"

    def _subnav_link(self, selector: str, name: str):
        # The label is wrapped in whitespace, so do not anchor the match.
        return self.page.locator(selector).filter(
            has_text=re.compile(re.escape(name), re.I)
        ).first

    def expect_redeem_and_balance(self) -> None:
        # Redeem and balance stay in the Gift Cards subnav.
        redeem = self._subnav_link(GiftCardsLocators.REDEEM_LINK, "Redeem Gift Cards")
        balance = self._subnav_link(GiftCardsLocators.BALANCE_LINK, "View Your Balance")
        expect(redeem).to_be_visible()
        expect(balance).to_be_visible()
