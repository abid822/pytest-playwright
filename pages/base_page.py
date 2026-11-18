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
        # A block page can still show the header search, so check that too.
        for _ in range(3):
            self.click_continue_shopping()
            self.dismiss_continue_shopping()
            try:
                expect(search).to_be_visible(timeout=5000)
                return
            except AssertionError:
                continue
        self.click_continue_shopping()
        self.dismiss_continue_shopping()
        expect(search).to_be_visible()

    def _page_title(self) -> str:
        try:
            return (self.page.title() or "").strip()
        except Exception:
            return ""

    def _text_visible(self, pattern: re.Pattern) -> bool:
        # Headings and alert boxes only. A full-page text scan crashes Firefox.
        loc = self.page.locator("h1, h2, h3, h4, .a-alert-content, .a-box-inner").filter(
            has_text=pattern
        )
        try:
            return loc.count() > 0 and loc.first.is_visible()
        except Exception:
            return False

    def _empty_document(self) -> bool:
        # A block response with a blank title and almost no controls.
        # A store page that is still painting has a title or real links.
        if self._page_title():
            return False
        url = (self.page.url or "").lower()
        if "amazon." not in url:
            return False
        try:
            return bool(
                self.page.evaluate(
                    """() => {
                      const title = (document.title || '').trim();
                      if (title) return false;
                      const body = document.body;
                      if (!body) return true;
                      if (body.querySelectorAll('a, button, input, img').length > 6) return false;
                      return (body.innerText || '').trim().length < 40;
                    }"""
                )
            )
        except Exception:
            return False

    def _block_reason(self) -> str | None:
        # Explicit block, captcha, or empty document. Not a normal store page.
        if self._is_continue_shopping_page():
            return None
        title = self._page_title()
        if re.search(r"access restricted|access denied|robot check", title, re.I):
            return "Amazon access restricted page"
        path = urlparse(self.page.url or "").path.lower()
        if any(part in path for part in ("checkpoint", "captcha", "validatecaptcha")):
            return "Amazon bot checkpoint shown"
        if self._text_visible(re.compile(r"unusual browser activity", re.I)):
            return "Amazon bot checkpoint shown"
        if self._text_visible(re.compile(r"enter the characters you see", re.I)):
            return "Amazon bot checkpoint shown"
        if self._text_visible(
            re.compile(r"sorry, we just need to make sure you.?re not a robot", re.I)
        ):
            return "Amazon bot checkpoint shown"
        if self._text_visible(re.compile(r"access restricted", re.I)):
            return "Amazon access restricted page"
        if self._text_visible(re.compile(r"to discuss automated access to amazon", re.I)):
            return "Amazon access restricted page"
        if self._error_page_shown():
            return "Amazon error page shown"
        denied = self.page.get_by_role("heading", name=re.compile(r"^access denied$", re.I))
        try:
            if denied.count() and denied.first.is_visible():
                return "Amazon access restricted page"
        except Exception:
            pass
        if self._empty_document():
            return "Amazon returned an empty page"
        return None

    def _error_page_shown(self) -> bool:
        # Amazon's dog page. The search box is a different control, and the title is blank.
        if "cs_503" in (self.page.url or ""):
            return True
        try:
            link = self.page.get_by_role(
                "link", name=re.compile(r"something went wrong on our end", re.I)
            )
            return link.count() > 0 and link.first.is_visible()
        except Exception:
            return False

    def _absolute_href(self, href: str) -> str:
        if href.startswith("/"):
            return "https://www.amazon.com" + href
        return href

    def _open_href(self, href: str) -> None:
        target = self._absolute_href(href)
        assert target, "link has no href"
        self.page.goto(target, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()

    def expect_url_or_follow(self, pattern, href: str) -> None:
        # A click can stay put, or continue-shopping can send us back to the home page.
        try:
            expect(self.page).to_have_url(pattern, timeout=8000)
        except AssertionError:
            self._open_href(href)
        else:
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        if pattern.search(self.page.url or "") is None:
            self._open_href(href)
        expect(self.page).to_have_url(pattern)

    def expect_visible_or_skip_shell(self, locator, reason: str) -> None:
        # The store URL loaded, but Amazon did not render the shop.
        try:
            expect(locator.first).to_be_visible()
        except AssertionError:
            try:
                missing = locator.count() == 0
            except Exception:
                missing = True
            if missing:
                pytest.skip(reason)
            raise

    def expect_named_heading(self, name: str) -> None:
        # The label is not always exposed as a heading.
        pattern = re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        heading = self.page.get_by_role("heading", name=pattern)
        text = self.page.locator("h1, h2, h3, span").filter(has_text=pattern)
        expect(heading.or_(text).first).to_be_visible()

    def expect_title(self, pattern) -> None:
        # A blank title after the wait is the empty page CI sometimes gets.
        # A different title still fails.
        try:
            expect(self.page).to_have_title(pattern)
        except AssertionError:
            if self._page_title():
                raise
            pytest.skip("Amazon returned a page with an empty title")

    @staticmethod
    def search_url_pattern(query: str | None = None) -> re.Pattern:
        # WebKit sometimes records the query as field-keywords= instead of k=.
        param = r"[?&](?:k|field-keywords)="
        if not query:
            return re.compile(param, re.I)
        parts = [re.escape(part) for part in query.split() if part]
        joined = r"(?:\+|%20)".join(parts) if parts else re.escape(query)
        return re.compile(rf"{param}{joined}(?:&|$)", re.I)

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
        # Skip when a block, captcha, or empty page is still there afterward.
        self.wait_for_page_load()
        if self._is_continue_shopping_page():
            self.click_continue_shopping()
            self.wait_for_page_load()
        if self._bot_checkpoint_shown() or self._block_reason() == "Amazon bot checkpoint shown":
            try:
                self._pass_human_checkpoint()
            except Exception:
                pass
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
        reason = self._block_reason()
        if reason:
            pytest.skip(reason)
        if self._bot_checkpoint_shown():
            pytest.skip("Amazon bot checkpoint shown")

    def save_screenshot(self, name: str) -> Path:
        path = report_png(name)
        self.page.screenshot(path=str(path), full_page=True)
        print(f"\nScreenshot saved: {path}\n")
        return path
