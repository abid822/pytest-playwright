import re

from playwright.sync_api import Page, expect

from locators.amazon_devices_locators import AmazonDevicesLocators
from pages.base_page import BasePage

# Section headings that stay on the Amazon Devices page. Deal tiles rotate.
CORE_CATEGORIES = [
    "Echo",
    "Amazon Alexa Tablets",
    "Home security",
    "Kindle",
]


class AmazonDevicesPage(BasePage):
    """Amazon Devices: store sections, then a priced Kindle e-reader."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _page_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^\s*Amazon Devices\s*$", re.I)
        )

    def _devices_ready(self) -> bool:
        # The store title says Amazon Devices, and the page heading has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Amazon Devices", title, re.I):
                return False
            heading = self._page_heading()
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_amazon_devices(self) -> None:
        # Step 1: Open the Amazon Devices store.
        # The first response is sometimes a shell with no sections.
        self.open(AmazonDevicesLocators.URL)
        for _ in range(2):
            if self._devices_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Amazon Devices store is showing, not a bot checkpoint.
        # The document title says "Amazon Devices".
        expect(self.page).to_have_url(re.compile(r"node=2102313011"))
        self.expect_title(re.compile(r"Amazon Devices", re.I))
        expect(self._page_heading().first).to_be_visible()

    def _section_heading(self, name: str):
        # The heading text can include surrounding whitespace.
        return self.page.get_by_role(
            "heading", name=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        )

    def expect_core_categories(self, names: list[str] | None = None) -> None:
        # Step 1: The Amazon Devices heading is on screen
        expect(self._page_heading().first).to_be_visible()
        # Step 2: Each core section is listed
        missing = []
        for name in names or CORE_CATEGORIES:
            heading = self._section_heading(name)
            try:
                expect(heading.first).to_be_visible()
            except AssertionError:
                missing.append(name)
        assert not missing, f"Missing Amazon Devices categories: {missing}"

    def _kindle_shop_link(self):
        # Several "Shop Kindle" links. Use one that is showing.
        matches = self.page.locator(AmazonDevicesLocators.KINDLE_SHOP_LINK).filter(
            has_text=re.compile(r"Shop Kindle", re.I)
        )
        for index in range(matches.count()):
            item = matches.nth(index)
            try:
                if item.is_visible():
                    return item
            except Exception:
                continue
        return matches.first

    def _kindle_heading(self):
        return self.page.get_by_role("heading", name=re.compile(r"Kindle", re.I))

    def _kindle_ready(self) -> bool:
        try:
            title = self.page.title() or ""
            if not re.search(r"Kindle", title, re.I):
                return False
            heading = self._kindle_heading()
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_kindle(self) -> None:
        # Step 1: Open Kindle from the devices page
        link = self._kindle_shop_link()
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        self.expect_url_or_follow(re.compile(r"kindle/shop"), href)
        # The click sometimes lands on a shell: right URL, empty title.
        # A reload paints the Kindle shop. A second goto of the same href does not.
        if not self._kindle_ready():
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"kindle/shop"))
        self.expect_title(re.compile(r"Kindle", re.I))
        expect(self._kindle_heading().first).to_be_visible()

    def expect_priced_product(self) -> None:
        # An e-reader card on the Kindle shop shows a dollar price.
        price = self.page.locator(AmazonDevicesLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"Kindle e-reader has no price: {text!r}"
        )
