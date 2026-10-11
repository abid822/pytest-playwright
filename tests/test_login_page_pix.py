import pytest

from utils.visual import compare_screenshot


@pytest.mark.login
def test_amazon_login_page_pixelmatch(login_page, sb_page):
    login_page.open_sign_in()
    compare_screenshot(
        sb_page,
        "baselines/amazon_login_form.png",
        locator=login_page.login_form(),
    )
