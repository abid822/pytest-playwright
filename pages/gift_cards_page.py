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
        self.product_title = page.locator(GiftCardsLocators.PRODUCT_TITLE)

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

    def _birthday_egift(self):
        # Amazon's own Birthday eGift, not a brand card that mentions a birthday.
        return self.page.locator(GiftCardsLocators.PRODUCT_LINK).filter(
            has_text=re.compile(r"Amazon eGift Card", re.I)
        ).filter(
            has_text=re.compile(r"\bBirthday\b", re.I)
        ).first

    def open_birthday_egift(self) -> None:
        # Step 1: Open a Birthday eGift card from the shop
        link = self._birthday_egift()
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        link.scroll_into_view_if_needed()
        link.click()
        # Step 2: If the click stays on the shop, follow the href
        try:
            expect(self.page).to_have_url(re.compile(r"/dp/", re.I), timeout=8000)
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, "Birthday eGift link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"/dp/", re.I))
        expect(self.page).to_have_title(re.compile(r"Gift Card", re.I))

    def expect_priced_egift(self) -> None:
        # The detail page names the card and shows a dollar price.
        expect(self.product_title).to_be_visible()
        expect(self.product_title).to_contain_text(re.compile(r"Gift Card", re.I))
        price = self.page.locator(GiftCardsLocators.PRICE).filter(
            has_text=re.compile(r"\$\s*\d")
        ).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), f"Birthday eGift has no price: {text!r}"
