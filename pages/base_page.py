import re

from playwright.sync_api import Page, expect

from config.settings import settings


class BasePage:
    """Shared browser helpers. All page objects inherit this."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str | None = None) -> None:
        # Step 1: Go to Amazon (or a custom URL)
        self.page.goto(url or settings.base_url)
        # Step 2: Confirm we landed on amazon.com
        expect(self.page).to_have_url(re.compile(r"amazon\.com", re.I))
