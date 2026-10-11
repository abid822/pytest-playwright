import pytest

from utils.visual import compare_screenshot


@pytest.mark.login
def test_amazon_login_page_pixelmatch(login_page, sb_page):
    # Step 1: Open the sign-in form
    login_page.open_sign_in()
    # Step 2: Compare the form screenshot to the baseline image
    compare_screenshot(
        sb_page,
        "baselines/amazon_login_form.png",
        locator=login_page.login_form(),
    )
