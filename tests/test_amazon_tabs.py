import pytest


@pytest.mark.smoke
@pytest.mark.tabs
def test_amazon_tabs(home_page):
    home_page.open_home()
    home_page.expect_core_tabs()
