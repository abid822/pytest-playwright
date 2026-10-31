import pytest


@pytest.mark.tabs
def test_nav_container(home_page):
    # Step 1: Open Amazon home
    home_page.open_home()
    # Step 2: Top nav container is visible
    home_page.expect_nav_container()
    # Step 3: More than a handful of tab links exist
    assert home_page.tab_links.count() > 5
