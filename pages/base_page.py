import re

from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from config.settings import report_png, settings
from locators.home_locators import HomeLocators


class BasePage:
    """Shared browser helpers. All page objects inherit this."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str | None = None) -> None:
        # Step 1: Go to Amazon (or a custom URL)
        self.page.goto(url or settings.base_url, wait_until="domcontentloaded")
        # Step 2: Confirm we landed on amazon.com
        self.wait_for_page_load()
        expect(self.page).to_have_url(re.compile(r"amazon\.com", re.I))
        # Step 3: A bot checkpoint or captcha skips the test. It is not clicked through.
        self.dismiss_continue_shopping()

    def wait_for_page_load(self) -> None:
        # domcontentloaded is the reliable point. Amazon often never goes idle.
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            return
        try:
            self.page.wait_for_load_state("load", timeout=8000)
        except Exception:
            pass

    def _bot_checkpoint_shown(self) -> bool:
        # /checkpoint/ or a captcha page. The test must not try to pass these.
        if re.search(r"/checkpoint/|captcha", self.page.url or "", re.I):
            return True
        try:
            captcha = self.page.locator(HomeLocators.CONTINUE_SHOPPING_BUTTON)
            return captcha.count() > 0 and captcha.first.is_visible()
        except Exception:
            return False

    def dismiss_continue_shopping(self) -> None:
        # Skip the test when Amazon shows a bot checkpoint or captcha.
        self.wait_for_page_load()
        if self._bot_checkpoint_shown():
            pytest.skip("Amazon bot checkpoint shown")

    def save_screenshot(self, name: str) -> Path:
        path = report_png(name)
        self.page.screenshot(path=str(path), full_page=True)
        print(f"\nScreenshot saved: {path}\n")
        return path
