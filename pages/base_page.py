import re

from pathlib import Path

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
        # Step 3: Pass the continue-shopping check when a fresh session gets one
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

    def _continue_button(self):
        # The captcha form, or the checkpoint page's Continue shopping submit.
        # A CSS filter stays off the accessibility tree, which is slow on Amazon.
        by_form = self.page.locator(HomeLocators.CONTINUE_SHOPPING_BUTTON)
        by_text = self.page.locator("button[type='submit'].a-button-text").filter(
            has_text=re.compile(r"^Continue(?: shopping)?$")
        )
        return by_form.or_(by_text)

    def _gate_continue_button(self):
        # On the checkpoint page the accessible name is reliable. WebKit
        # sometimes omits type=submit or the a-button-text class.
        by_role = self.page.get_by_role(
            "button", name=re.compile(r"^Continue(?: shopping)?$", re.I)
        )
        return self._continue_button().or_(by_role)

    def _check_human_box(self) -> None:
        # /checkpoint/validate leaves Continue shopping disabled until this box is checked.
        name = re.compile(r"I am human", re.I)
        scopes = [self.page]
        scopes.extend(frame for frame in self.page.frames if frame != self.page.main_frame)
        for scope in scopes:
            box = scope.get_by_role("checkbox", name=name)
            if box.count() == 0:
                continue
            target = box.first
            try:
                target.scroll_into_view_if_needed(timeout=3000)
            except Exception:
                pass
            try:
                if target.is_checked():
                    return
            except Exception:
                pass
            try:
                target.check(timeout=5000)
                return
            except Exception:
                pass
            label = scope.get_by_text(re.compile(r"^I am human$", re.I))
            try:
                if label.count() and label.first.is_visible():
                    label.first.click(timeout=5000)
                    return
            except Exception:
                continue

    def _shopping_gate_present(self) -> bool:
        if re.search(r"checkpoint|validateCaptcha", self.page.url):
            return True
        try:
            button = self._continue_button()
            return button.count() > 0 and button.first.is_visible()
        except Exception:
            return False

    def dismiss_continue_shopping(self) -> None:
        # No gate: return immediately so a normal page load stays fast.
        self.wait_for_page_load()
        try:
            on_gate = self._shopping_gate_present()
        except Exception:
            return
        if not on_gate:
            return
        # The validate page keeps the submit button disabled until the box is checked.
        self._check_human_box()
        button = self._gate_continue_button()
        try:
            button.first.wait_for(state="visible", timeout=5000)
        except Exception:
            return
        target = button.first
        # WebKit often paints this submit control disabled until the checkbox settles.
        try:
            expect(target).to_be_visible(timeout=5000)
            expect(target).to_be_enabled(timeout=8000)
            target.click(timeout=8000)
        except Exception:
            try:
                target.evaluate(
                    """el => {
                        const form = el.closest('form');
                        el.disabled = false;
                        el.removeAttribute('disabled');
                        try {
                            if (form) {
                                form.submit();
                            } else {
                                el.click();
                            }
                        } catch (err) {
                            el.click();
                        }
                    }"""
                )
            except Exception:
                return
        self.wait_for_page_load()
        try:
            expect(target).to_be_hidden(timeout=8000)
        except AssertionError:
            pass

    def save_screenshot(self, name: str) -> Path:
        path = report_png(name)
        self.page.screenshot(path=str(path), full_page=True)
        print(f"\nScreenshot saved: {path}\n")
        return path
