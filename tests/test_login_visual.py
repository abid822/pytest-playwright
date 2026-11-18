import pytest

from config.settings import settings
from utils.visual import compare_screenshot


@pytest.mark.login_visual
@pytest.mark.chromium_only
@pytest.mark.desktop_only
@pytest.mark.skipif(
    settings.browser != "chromium",
    reason=(
        "Pixel baseline baselines/amazon_login_form.png is Chromium-only. "
        "Firefox and WebKit draw the Amazon sign-in card differently."
    ),
)
def test_login_form_visual(login_page, sb_page):
    # Step 1: Open the sign-in form
    login_page.open_sign_in()
    # Step 2: The email box autofocuses. That blue ring is not in the baseline.
    login_page.defocus_email()
    # Step 3: Compare the form. The email box is masked so a leftover ring still matches.
    compare_screenshot(
        sb_page,
        "baselines/amazon_login_form.png",
        locator=login_page.login_form(),
        mask=[login_page.email_field()],
    )
