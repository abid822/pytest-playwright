import re

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
        # Invalid email / auth error banner
        self.error = page.locator(LoginLocators.INVALID_EMAIL_ALERT)
        self.agreement = page.get_by_text(re.compile(r"By continuing", re.I))
        self.need_help = page.get_by_role("button", name=re.compile(r"Need help", re.I)).or_(
            page.get_by_text(re.compile(r"Need help", re.I))
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
            if not href:
                href = sign_link.get_attribute("href") or ""
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, "Sign in control has no href"
            self.page.goto(href)
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

    def submit_email(self, email: str) -> None:
        # Step 1: Enter email / phone
        self.email.fill(email)
        # Step 2: Click Continue
        self.continue_btn.click()

    def expect_invalid_email_error(self) -> None:
        # Error banner should mention invalid / incorrect email
        expect(self.error).to_be_visible()
        expect(self.error).to_contain_text(re.compile(r"invalid|incorrect|e-?mail", re.I))

    def expect_sign_in_helpers(self) -> None:
        # Legal text and helper links on the sign-in form
        expect(self.agreement).to_be_visible()
        expect(self.need_help.first).to_be_visible()
        expect(self.buying_for_work.first).to_be_visible()

    def login_form(self):
        # Sign-in card (email field + Continue), used by the pixel test
        return self.page.locator(".a-box.ax-content-container, #claim-collection-container").first
