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
