import pytest


@pytest.mark.login
@pytest.mark.smoke
def test_amazon_invalid_login(login_page):
    # Step 1: Open the sign-in form from the header
    login_page.open_sign_in()
    # Step 2: Submit a bad email (missing @)
    login_page.submit_email("invalidemailgmail.com")
    # Step 3: Error message plus helper links should show
    login_page.expect_invalid_email_error()
    login_page.expect_sign_in_helpers()
