import re

import pytest
from playwright.sync_api import Page, expect

from locators.customer_service_locators import CustomerServiceLocators
from pages.base_page import BasePage

# Topics that stay on the Customer Service hub.
CORE_TOPICS = [
    "Where's my stuff",
    "Shipping and Delivery",
    "Returns, Refunds and Product Support",
    "Managing Your Account",
]


class CustomerServicePage(BasePage):
    """Amazon Customer Service: help search and topic articles."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_input = page.locator(CustomerServiceLocators.SEARCH_INPUT)
        self.topics = page.locator(CustomerServiceLocators.TOPICS)
        self.active_articles = page.locator(CustomerServiceLocators.ACTIVE_ARTICLES)

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

    def expect_core_topics(self, names: list[str] | None = None) -> None:
        # Step 1: The topic list is on the page
        expect(self.topics).to_be_visible()
        self.topics.scroll_into_view_if_needed()
        # Step 2: Each core topic is listed
        missing = []
        for name in names or CORE_TOPICS:
            label = self._topic_label(name)
            if label.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Customer Service topics: {missing}"

    def _topic_label(self, name: str):
        return self.topics.locator("label").filter(
            has_text=re.compile(rf"^{re.escape(name)}$")
        )

    def open_topic(self, name: str) -> None:
        # Step 1: Choose that topic from the list
        label = self._topic_label(name).first
        expect(label).to_be_visible()
        label.scroll_into_view_if_needed()
        input_id = label.get_attribute("for") or ""
        assert input_id, f"{name} topic has no input"
        label.click()
        # Step 2: The topic radio is selected
        expect(self.page.locator(f"#{input_id}")).to_be_checked()

    def expect_topic_articles(self, names: list[str]) -> None:
        # The open topic lists articles, including one of the expected titles.
        expect(self.active_articles.first).to_be_visible()
        found = []
        count = min(self.active_articles.count(), 16)
        for i in range(count):
            text = " ".join((self.active_articles.nth(i).inner_text() or "").split())
            if text:
                found.append(text)
        assert len(found) >= 2, f"Topic listed too few articles: {found}"
        matched = [name for name in names if name in found]
        assert matched, f"Topic articles did not include {names}: {found}"
