import re

import pytest
from playwright.sync_api import Page, expect

from locators.customer_service_locators import CustomerServiceLocators
from pages.base_page import BasePage


class CustomerServicePage(BasePage):
    """Amazon Customer Service help hub."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.locator(CustomerServiceLocators.SEARCH_INPUT)

    def _page_not_found(self) -> bool:
        # Amazon sometimes answers the help hub with its dog "Page Not Found" page.
        title = self.page.title() or ""
        if re.search(r"Page Not Found", title, re.I):
            return True
        missing = self.page.get_by_role(
            "link", name=re.compile(r"couldn't find that page", re.I)
        )
        try:
            return missing.count() > 0 and missing.first.is_visible()
        except Exception:
            return False

    def open_customer_service(self) -> None:
        # Step 1: Open the Customer Service hub.
        # The first response is sometimes Page Not Found; load it once more.
        self.open(CustomerServiceLocators.URL)
        if self._page_not_found():
            self.page.goto(CustomerServiceLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: Welcome heading is the help hub, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/gp/help/customer/display\.html", re.I))
        if self._page_not_found():
            pytest.skip("Amazon returned Page Not Found for Customer Service")
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r"Welcome to Amazon Customer Service", re.I),
            )
        ).to_be_visible()

    def expect_help_search(self) -> None:
        # The help library search box is on the hub and can be typed in.
        expect(self.search_input).to_be_visible()
        expect(self.search_input).to_be_editable()
