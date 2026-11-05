import re

from playwright.sync_api import expect

from locators.find_a_gift_locators import FindAGiftLocators
from pages.base_page import BasePage

# Shop headings that stay on the Find a Gift landing page.
SHOP_SECTIONS = [
    "Shop by Occasion",
    "Shop by Interest",
    "Shop by Recipient",
]

# Occasion tiles that stay on the landing page. Holiday tiles rotate.
OCCASIONS = [
    "Birthdays",
    "Baby Shower",
    "Wedding & Engagement",
    "Graduation",
]

RECIPIENTS = [
    "For Her",
    "For Him",
    "For Teens",
    "For Kids",
]


class FindAGiftPage(BasePage):
    """Amazon Find a Gift: shop sections, then a priced birthday gift."""

    def _gift_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Gift Shop$", re.I)
        )

    def _gift_ready(self) -> bool:
        # The document title is sometimes blank. The Gift Shop heading is the check.
        heading = self._gift_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_find_a_gift(self) -> None:
        # Step 1: Open the Gift Shop.
        # The first response is sometimes a shell with no heading.
        self.open(FindAGiftLocators.URL)
        if not self._gift_ready():
            self.page.goto(FindAGiftLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Gift Shop is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"node=206764924011"))
        expect(self._gift_heading().first).to_be_visible()

    def expect_shop_sections(self, names: list[str] | None = None) -> None:
        # Each shop-by heading is on the landing page.
        missing = []
        for name in names or SHOP_SECTIONS:
            heading = self.page.get_by_role(
                "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
            )
            if heading.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Find a Gift sections: {missing}"

    def _named_link(self, name: str):
        return self.page.locator(FindAGiftLocators.OCCASION_LINK).filter(
            has_text=re.compile(rf"^{re.escape(name)}$", re.I)
        )

    def expect_occasions(self, names: list[str] | None = None) -> None:
        # Occasion tiles stay under Shop by Occasion.
        missing = []
        for name in names or OCCASIONS:
            if self._named_link(name).count() == 0:
                missing.append(name)
        assert not missing, f"Missing Find a Gift occasions: {missing}"

    def expect_recipients(self, names: list[str] | None = None) -> None:
        # Recipient tiles stay under Shop by Recipient.
        missing = []
        for name in names or RECIPIENTS:
            if self._named_link(name).count() == 0:
                missing.append(name)
        assert not missing, f"Missing Find a Gift recipients: {missing}"

    def open_birthdays(self) -> None:
        # Step 1: The Birthdays tile is on the shop.
        # A carousel click can stay put, so follow the href in this tab.
        link = self._named_link("Birthdays").first
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        if href.startswith("/"):
            href = "https://www.amazon.com" + href
        assert href, "Birthdays link has no href"
        node = re.search(r"node=(\d+)", href)
        assert node, f"Birthdays link has no node: {href}"
        self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # Step 2: Birthday gifts are listed
        expect(self.page).to_have_url(re.compile(rf"node={node.group(1)}"))
        expect(self.page).to_have_title(re.compile(r"Birthday", re.I))
        heading = self.page.get_by_role(
            "heading", name=re.compile(r"^Birthdays$", re.I)
        )
        if heading.count() > 0:
            expect(heading.first).to_be_visible()
            return
        expect(self.page.locator(FindAGiftLocators.RESULT).first).to_be_visible()

    def expect_priced_gift(self) -> None:
        # The birthday list names a gift and shows a dollar price.
        card = self.page.locator(FindAGiftLocators.RESULT).filter(
            has_text=re.compile(r"\$\s*\d")
        ).first
        card.scroll_into_view_if_needed()
        expect(card).to_be_visible()
        title = card.locator(FindAGiftLocators.PRODUCT_TITLE).filter(
            has_text=re.compile(r"[A-Za-z]{3}")
        ).first
        expect(title).to_be_visible()
        text = " ".join((title.inner_text() or "").split())
        assert re.search(r"[A-Za-z]{3}", text), f"Birthday gift has no title: {text!r}"
        price = card.locator(FindAGiftLocators.PRICE).filter(
            has_text=re.compile(r"\$\s*\d")
        ).first
        expect(price).to_be_attached()
        amount = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", amount), f"Birthday gift has no price: {amount!r}"
