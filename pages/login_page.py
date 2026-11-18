import re

import pytest
from playwright.sync_api import Page, expect

from locators.login_locators import LoginLocators
from pages.home_page import HomePage


class LoginPage(HomePage):
    """Amazon sign-in: open the form, submit email, check errors."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Account menu in the header
        self.account_list = page.locator(LoginLocators.ACCOUNT_LIST)
        # Sign in button inside the account flyout
        self.sign_in = page.locator(LoginLocators.SIGN_IN_BUTTON)
        # Email / mobile field on the login form
        self.email = page.locator(LoginLocators.ENTER_MOBILE_OR_EMAIL)
        # Continue (span#continue wraps an input on Amazon)
        self.continue_btn = page.locator(LoginLocators.CONTINUE_BUTTON).first
        # Password field on the second sign-in step
        self.password = page.locator(LoginLocators.PASSWORD)
        self.password_submitted = False
        # Sign in after the password is entered
        self.sign_in_submit = page.locator(LoginLocators.SIGN_IN_SUBMIT)
        # Unknown email: Amazon offers account creation instead of a password
        self.new_account = page.get_by_role(
            "heading", name=re.compile(r"new to Amazon", re.I)
        ).or_(page.get_by_role("button", name=re.compile(r"Proceed to create an account", re.I)))
        # Invalid email / auth error banner
        self.error = page.locator(LoginLocators.INVALID_EMAIL_ALERT)
        self.agreement = page.get_by_text(re.compile(r"By continuing", re.I))
        # "Need help?" is an expander link or a span, not always a button.
        self.need_help = page.locator("a, button, span").filter(
            has_text=re.compile(r"^\s*Need help\??\s*$", re.I)
        )
        self.buying_for_work = page.get_by_role(
            "link", name=re.compile(r"Buying for work|Create a free business account", re.I)
        )

    def open_sign_in(self) -> None:
        # Step 1: Open Amazon home
        self.open_home()
        # Mobile header has a Sign in link. Desktop uses Account & Lists.
        if self.account_list.count() == 0 or not self.account_list.is_visible():
            self._open_mobile_sign_in()
            return
        # Step 2: Hover Account & Lists and click Sign in
        href = self.account_list.get_attribute("href") or ""
        box = self.account_list.bounding_box()
        if box:
            self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        else:
            self.account_list.hover()
        sign_link = self.sign_in.locator("a").first
        if sign_link.count() and sign_link.is_visible():
            sign_link.click()
        else:
            self.account_list.click()
        # Step 3: If the flyout click stays on the home page, open the sign-in URL
        try:
            expect(self.email).to_be_visible(timeout=6000)
        except AssertionError:
            self.dismiss_continue_shopping()
            if not href and sign_link.count():
                try:
                    href = sign_link.get_attribute("href", timeout=2000) or ""
                except Exception:
                    href = ""
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, "Sign in control has no href"
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
            expect(self.email).to_be_visible()

    def _open_mobile_sign_in(self) -> None:
        # Header link only. The footer also has a Sign in link.
        link = self.page.locator("#nav-main").get_by_role(
            "link", name=re.compile(r"^Sign in\b", re.I)
        )
        expect(link.first).to_be_visible()
        link.first.click()
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.email).to_be_visible()

    def email_field(self):
        # The visible email box. A hidden duplicate can sit earlier in the DOM.
        field = self.email
        for i in range(field.count()):
            item = field.nth(i)
            if item.is_visible():
                return item
        return field.first

    def defocus_email(self) -> None:
        # Autofocus draws a blue ring that is not part of the pixel baseline.
        field = self.email_field()
        expect(field).to_be_visible()
        field.evaluate(
            """el => {
              el.blur();
              const nodes = [el, el.parentElement].filter(Boolean);
              for (const node of nodes) {
                node.style.outline = 'none';
                node.style.boxShadow = 'none';
              }
              if (document.activeElement && document.activeElement.blur) {
                document.activeElement.blur();
              }
            }"""
        )

    def _challenge_in_frame(self, frame) -> bool:
        # Image puzzle Amazon shows after many fake sign-ins.
        heading = frame.get_by_role(
            "heading", name=re.compile(r"solve this puzzle", re.I)
        )
        if heading.count() and heading.first.is_visible():
            return True
        puzzle = frame.get_by_role(
            "button", name=re.compile(r"get an audio puzzle|get a new puzzle", re.I)
        )
        return puzzle.count() > 0 and puzzle.first.is_visible()

    def skip_if_bot_challenge(self) -> None:
        # The puzzle cannot be solved here. Skip instead of failing the sign-in check.
        for frame in self.page.frames:
            try:
                if self._challenge_in_frame(frame):
                    pytest.skip("Amazon bot challenge shown")
            except pytest.skip.Exception:
                raise
            except Exception:
                continue

    def _settle_after_submit(self) -> None:
        # The checkpoint page often arrives after Continue, not before it.
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
        self.dismiss_continue_shopping()
        self.skip_if_bot_challenge()

    def _expect_login_step(self) -> None:
        step = self.password.or_(self.error).or_(self.new_account)
        try:
            expect(step.first).to_be_visible()
        except AssertionError:
            self._settle_after_submit()
            expect(step.first).to_be_visible()
        self.skip_if_bot_challenge()

    def submit_email(self, email: str) -> None:
        # Step 1: Enter email / phone
        self.email_field().fill(email)
        # Step 2: Click Continue
        self.continue_btn.click()

    def _visible_password(self):
        # Any visible password box, not only #ap_password
        field = self.password.or_(self.page.locator("input[type='password']"))
        for i in range(field.count()):
            if field.nth(i).is_visible():
                return field.nth(i)
        return None

    def _login_step_visible(self) -> bool:
        # Password field, an error, or the create-account prompt.
        step = self.password.or_(self.error).or_(self.new_account).first
        try:
            return step.count() > 0 and step.is_visible()
        except Exception:
            return False

    def _back_on_home(self) -> bool:
        # Continue shopping leaves sign-in and opens the store home page.
        url = (self.page.url or "").lower()
        if "/ap/signin" in url or "openid" in url:
            return False
        try:
            return self.search_input.is_visible()
        except Exception:
            return False

    def submit_credentials(self, username: str, password: str) -> None:
        # Step 1: Enter the username and continue
        self.password_submitted = False
        self.submit_email(username)
        # Step 2: Pass the human checkbox when Amazon shows it.
        # Continue shopping sends us back to the home page, so sign in once more.
        self._settle_after_submit()
        if not self._login_step_visible() and self._back_on_home():
            self.open_sign_in()
            self.submit_email(username)
            self._settle_after_submit()
        # Step 3: Error, create-account prompt, or a password field.
        # A checkpoint that lands during this wait is skipped.
        self._expect_login_step()
        password_box = self._visible_password()
        if password_box is None:
            return
        password_box.fill(password)
        self.password_submitted = True
        # Step 4: Submit the password. Do not start account creation.
        if self.sign_in_submit.is_visible():
            self.sign_in_submit.click()
        else:
            password_box.press("Enter")
        self._settle_after_submit()

    def expect_invalid_email_error(self) -> None:
        # Error banner should mention invalid / incorrect email.
        # A checkpoint or puzzle in its place is a block, not a missing banner.
        try:
            expect(self.error).to_be_visible()
        except AssertionError:
            self._settle_after_submit()
            expect(self.error).to_be_visible()
        self.skip_if_bot_challenge()
        expect(self.error).to_contain_text(re.compile(r"invalid|incorrect|e-?mail", re.I))

    def expect_login_rejected(self, username: str) -> None:
        # A puzzle or checkpoint after submit is a block, not a wrong assertion.
        self.skip_if_bot_challenge()
        # A submitted password must be rejected. Do not click "create an account".
        if self.password_submitted:
            try:
                expect(self.error).to_be_visible()
            except AssertionError:
                self._settle_after_submit()
                expect(self.error).to_be_visible()
            expect(self.error).to_contain_text(
                re.compile(r"invalid|incorrect|password|cannot find|problem|account", re.I)
            )
            return
        # Unknown email: the create-account page must show this username.
        try:
            expect(self.new_account.first).to_be_visible()
        except AssertionError:
            self._settle_after_submit()
            expect(self.new_account.first).to_be_visible()
        expect(self.page.get_by_text(username, exact=False).first).to_be_visible()
        expect(
            self.page.get_by_role("button", name=re.compile(r"Proceed to create an account", re.I))
        ).to_be_visible()

    def expect_sign_in_helpers(self) -> None:
        # Legal text and helper links on the sign-in form.
        self.skip_if_bot_challenge()
        expect(self.agreement.first).to_be_visible()
        self.agreement.first.scroll_into_view_if_needed()
        help_control = self.need_help.locator("visible=true")
        try:
            expect(help_control.first).to_be_visible()
        except AssertionError:
            self._settle_after_submit()
            if help_control.count():
                help_control.first.scroll_into_view_if_needed()
            expect(help_control.first).to_be_visible()
        expect(self.buying_for_work.first).to_be_visible()

    def login_form(self):
        # Sign-in card (email field + Continue), used by the pixel test
        return self.page.locator(".a-box.ax-content-container, #claim-collection-container").first
