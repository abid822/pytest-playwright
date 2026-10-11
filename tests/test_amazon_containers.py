import pytest


@pytest.mark.tabs
def test_amazon_tabs_containers(home_page):
    home_page.open_home()
    home_page.expect_nav_container()
    assert home_page.tab_links.count() > 5
