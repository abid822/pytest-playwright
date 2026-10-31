import pytest


@pytest.mark.smoke
@pytest.mark.tabs
def test_nav_tabs(home_page):
    # Step 1: Open Amazon home
    home_page.open_home()
    # Step 2: Core tabs (Best Sellers, Today's Deals, Prime, Sell) are present
    home_page.expect_core_tabs()
