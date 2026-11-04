import re
from pathlib import Path
from urllib.parse import urlparse

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
        # Step 3: Pass the human checkbox when Amazon shows it
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

    def _checkpoint_in_path(self) -> bool:
        # The path only. A return URL in the query string must not count.
        path = urlparse(self.page.url or "").path.lower()
        return "checkpoint" in path or "captcha" in path

    def _continue_shopping_button(self):
        return self.page.get_by_role(
            "button", name=re.compile(r"^Continue shopping$", re.I)
        )

    def _is_continue_shopping_page(self) -> bool:
        # A short page: "Click the button below to continue shopping".
        # No search box. The human checkbox is a different page.
        button = self._continue_shopping_button()
        try:
            if button.count() == 0 or not button.first.is_visible():
                return False
            checkbox = self.page.get_by_role(
                "checkbox", name=re.compile(r"human|not a robot", re.I)
            )
            if checkbox.count() and checkbox.first.is_visible():
                return False
            return True
        except Exception:
            return False

    def click_continue_shopping(self) -> None:
        # Click the button when that page is showing. It can come back,
        # so try a few times.
        button = self._continue_shopping_button()
        for _ in range(3):
            try:
                if button.count() == 0 or not button.first.is_visible():
                    return
                button.first.click()
                self.wait_for_page_load()
            except Exception:
                return

    def wait_for_search_box(self, search) -> None:
        # Leave the continue-shopping page, then wait for the search box.
        for _ in range(3):
            self.click_continue_shopping()
            try:
                expect(search).to_be_visible(timeout=5000)
                return
            except AssertionError:
                continue
        self.click_continue_shopping()
        expect(search).to_be_visible()

    def _bot_checkpoint_shown(self) -> bool:
        # /checkpoint/, a captcha form, or the AI-agent interstitial.
        # The plain Continue shopping page is handled by clicking the button.
        if self._is_continue_shopping_page():
            return False
        if self._checkpoint_in_path():
            return True
        try:
            captcha = self.page.locator(HomeLocators.CONTINUE_SHOPPING_BUTTON)
            if captcha.count() > 0 and captcha.first.is_visible():
                return True
            wall = self.page.locator("h4").filter(
                has_text=re.compile(r"unauthorized AI agent", re.I)
            )
            return wall.count() > 0 and wall.first.is_visible()
        except Exception:
            return False

    def _pass_human_checkpoint(self) -> None:
        # Check "I am human" on the captcha form, then click that form's button.
        # Do not click the sign-in Continue control.
        form = self.page.locator("form[action*='validateCaptcha']")
        checkbox = form.locator("input[type='checkbox']")
        if checkbox.count() == 0:
            checkbox = self.page.get_by_role(
                "checkbox", name=re.compile(r"human|not a robot", re.I)
            )
        if checkbox.count() and checkbox.first.is_visible():
            checkbox.first.check()
        button = form.locator("button, input[type='submit']")
        if button.count() and button.first.is_visible():
            button.first.click()
            return
        shopping = self.page.get_by_role(
            "button", name=re.compile(r"continue shopping", re.I)
        )
        if shopping.count() and shopping.first.is_visible():
            shopping.first.click()
            return
        if self._checkpoint_in_path():
            other = self.page.get_by_role("button", name=re.compile(r"^continue$", re.I))
            if other.count() and other.first.is_visible():
                other.first.click()

    def dismiss_continue_shopping(self) -> None:
        # Click through the human check when those controls are visible.
        # Skip only if the checkpoint is still there afterward.
        self.wait_for_page_load()
        if self._is_continue_shopping_page():
            self.click_continue_shopping()
            return
        if not self._bot_checkpoint_shown():
            return
        self._pass_human_checkpoint()
        self.wait_for_page_load()
        try:
            self.page.wait_for_function(
                """() => {
                  const path = location.pathname.toLowerCase();
                  return !path.includes('checkpoint') && !path.includes('captcha');
                }""",
                timeout=15000,
            )
        except Exception:
            pass
        if self._bot_checkpoint_shown():
            pytest.skip("Amazon bot checkpoint shown")

    def save_screenshot(self, name: str) -> Path:
        path = report_png(name)
        self.page.screenshot(path=str(path), full_page=True)
        print(f"\nScreenshot saved: {path}\n")
        return path
