import pytest

from pages.footer_page import FooterPage


@pytest.mark.desktop_only
@pytest.mark.footer
def test_footer_back_to_top_returns_to_the_header(footer_page: FooterPage):
    """Opens the home footer, checks the help links, and uses Back to top."""
    # Step 1: Open Amazon home
    footer_page.open_home()
    # Step 2: Footer columns and the help links are listed
    footer_page.expect_footer_columns()
    footer_page.expect_help_links()
    # Step 3: Scroll to the bottom of the page
    footer_page.scroll_to_bottom()
    # Step 4: Back to top returns to the header
    footer_page.click_back_to_top()
