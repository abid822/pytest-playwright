import pytest

from playwright.sync_api import expect  # <--- Import this!
from locators.amazon_locators import AmazonHomeLocators
from locators.amazon_login_pg_locators import AmazonLoginLocators
from pages.amazon_login_actions import AmazonLoginActions

@pytest.mark.login

def test_amazon_invalid_login(sb_page):
    # 1. Give the browser to your actions class
    actions = AmazonLoginActions(sb_page)
    # 2. CALL YOUR SETUP STEPS! (Explicitly, with parentheses)
    actions.navigate_to_login_screen()

    # STEP 1: Enter invalid email
    print("--- Step 1: Entering invalid email ---")
    email_input = sb_page.locator(AmazonLoginLocators.ENTER_MOBILE_OR_EMAIL)
    expect(email_input).to_be_visible()
    email_input.fill("invalidemailgmail.com")
    
    sb_page.locator(AmazonLoginLocators.CONTINUE_BUTTON).click()

    # STEP 2: Verify error message appears
    print("--- Step 2: Verifying error message ---")
    error_message = sb_page.locator(AmazonLoginLocators.Invalid_EMAIL_alert)
    
    # This replaces your entire if/else block!
    expect(error_message).to_be_visible()
    
    # We can also verify the EXACT text of the error to be extra safe
    expect(error_message).to_contain_text(sb_page.locator(AmazonLoginLocators.Invalid_EMAIL_alert_path).inner_text().strip())

    # STEP 3: Verify agreement text is visible
    print("--- Step 3: Verifying agreement text ---")
    agreement_text = sb_page.locator(AmazonLoginLocators.AGREEMENT_TEXT)
    expect(agreement_text).to_be_visible()
    print(sb_page.locator(AmazonLoginLocators.AGREEMENT_TEXT).inner_text().strip())

    # STEP 4: Verify "Need Help?" link is visible
    print("--- Step 4: Verifying 'Need Help?' link ---")
    need_help_link = sb_page.locator(AmazonLoginLocators.NEED_HELP_LINK)
    expect(need_help_link).to_be_visible()
    print(sb_page.locator(AmazonLoginLocators.NEED_HELP_LINK).inner_text().strip())

    # STEP 5: Verify "Buying for Work" link is visible
    print("--- Step 5: Verifying 'Buying for Work' link ---")
    buying_for_work_link = sb_page.locator(AmazonLoginLocators.BUYING_FOR_WORK_LINK)
    expect(buying_for_work_link).to_be_visible()
    print(sb_page.locator(AmazonLoginLocators.BUYING_FOR_WORK_LINK).inner_text().strip())
    