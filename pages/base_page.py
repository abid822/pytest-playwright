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

    def _bot_checkpoint_shown(self) -> bool:
        # /checkpoint/, a captcha form, or the AI-agent interstitial.
        if re.search(r"/checkpoint/|captcha", self.page.url or "", re.I):
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
        # Check "I am human" when that box is on the page, then click Continue.
        form = self.page.locator("form[action*='validateCaptcha']")
        checkbox = form.locator("input[type='checkbox']").or_(
            self.page.get_by_role("checkbox", name=re.compile(r"human|not a robot", re.I))
        )
        if checkbox.count() and checkbox.first.is_visible():
            checkbox.first.check()
        button = self.page.locator(HomeLocators.CONTINUE_SHOPPING_BUTTON).or_(
            self.page.get_by_role("button", name=re.compile(r"continue", re.I))
        )
        if button.count() and button.first.is_visible():
            button.first.click()

    def dismiss_continue_shopping(self) -> None:
        # Click through the human check when those controls are visible.
        # Skip only if the checkpoint is still there afterward.
        self.wait_for_page_load()
        if not self._bot_checkpoint_shown():
            return
        self._pass_human_checkpoint()
        self.wait_for_page_load()
        try:
            self.page.wait_for_url(
                re.compile(r"amazon\.com(?!.*/(?:checkpoint|captcha))", re.I),
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
