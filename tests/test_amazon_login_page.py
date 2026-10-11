import pytest


@pytest.mark.login
@pytest.mark.smoke
def test_amazon_invalid_login(login_page):
    login_page.open_sign_in()
    login_page.submit_email("invalidemailgmail.com")
    login_page.expect_invalid_email_error()
    login_page.expect_sign_in_helpers()
