import pytest

from pages.footer_page import FooterPage


@pytest.mark.desktop_only
@pytest.mark.footer
def test_footer_back_to_top_returns_to_the_header(footer_page: FooterPage):
    """Opens the home footer. Classic columns use Back to top. The short legal card checks its links."""
    # Step 1: Open Amazon home
    footer_page.open_home()
    # Step 2: Classic four columns, or the shorter legal card Amazon sometimes serves
    if footer_page.footer_kind() == "classic":
        footer_page.expect_footer_columns()
        footer_page.expect_help_links()
    else:
        footer_page.expect_compact_footer()
    # Step 3: Back to top returns to the header when that control is on the page
    if footer_page.has_back_to_top():
        footer_page.scroll_to_bottom()
        footer_page.click_back_to_top()
