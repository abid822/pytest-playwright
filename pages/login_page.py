import re

from playwright.sync_api import Page, expect

from locators.amazon_login_pg_locators import AmazonLoginLocators
from pages.home_page import HomePage


class LoginPage(HomePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.account_list = page.locator(AmazonLoginLocators.ACCOUNT_LIST)
        self.sign_in = page.locator(AmazonLoginLocators.SIGN_IN_BUTTON)
        self.email = page.locator(AmazonLoginLocators.ENTER_MOBILE_OR_EMAIL)
        self.continue_btn = page.locator("#continue").locator("input, button").first
        self.error = page.locator(AmazonLoginLocators.Invalid_EMAIL_alert)
        self.agreement = page.get_by_text(re.compile(r"By continuing", re.I))
        self.need_help = page.get_by_role("button", name=re.compile(r"Need help", re.I)).or_(
            page.get_by_text(re.compile(r"Need help", re.I))
        )
        self.buying_for_work = page.get_by_role(
            "link", name=re.compile(r"Buying for work|Create a free business account", re.I)
        )

    def open_sign_in(self) -> None:
        self.open_home()
        self.account_list.hover()
        expect(self.sign_in).to_be_visible()
        self.sign_in.click()
        expect(self.email).to_be_visible()

    def submit_email(self, email: str) -> None:
        self.email.fill(email)
        self.continue_btn.click()

    def expect_invalid_email_error(self) -> None:
        expect(self.error).to_be_visible()
        expect(self.error).to_contain_text(re.compile(r"invalid|incorrect|e-?mail", re.I))

    def expect_sign_in_helpers(self) -> None:
        expect(self.agreement).to_be_visible()
        expect(self.need_help.first).to_be_visible()
        expect(self.buying_for_work.first).to_be_visible()

    def login_form(self):
        return self.page.locator("#authportal-main-section, form[name='signIn'], #ap_email_login").first
