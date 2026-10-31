import re

from pathlib import Path

from playwright.sync_api import Page, expect

from config.settings import ROOT, settings
from locators.home_locators import HomeLocators


class BasePage:
    """Shared browser helpers. All page objects inherit this."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str | None = None) -> None:
        # Step 1: Go to Amazon (or a custom URL)
        self.page.goto(url or settings.base_url)
        # Step 2: Confirm we landed on amazon.com
        expect(self.page).to_have_url(re.compile(r"amazon\.com", re.I))
        # Step 3: Pass the continue-shopping check when a fresh session gets one
        self.dismiss_continue_shopping()

    def dismiss_continue_shopping(self) -> None:
        button = self.page.locator(HomeLocators.CONTINUE_SHOPPING_BUTTON)
        if button.count() == 0 or not button.first.is_visible():
            return
        button.first.click()
        expect(button).to_be_hidden()

    def save_screenshot(self, name: str) -> Path:
        reports = ROOT / "reports"
        reports.mkdir(exist_ok=True)
        path = reports / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        print(f"\nScreenshot saved: {path}\n")
        return path
