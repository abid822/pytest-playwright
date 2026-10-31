import json
from pathlib import Path

import pytest
from playwright.sync_api import expect


@pytest.mark.tabs
@pytest.mark.smoke
def test_nav_hamburger(home_page):
    # Step 1: Open Amazon and click the hamburger / All menu
    home_page.open_home()
    home_page.open_hamburger_menu()

    # Step 2: Core labels must be present. Other JSON labels and extra Amazon items are printed, not failed
    data_file = Path(__file__).parent.parent / "data" / "hamburger_menu.json"
    expected = json.loads(data_file.read_text())
    home_page.expect_menu_contains(expected)

    # Step 3: Confirm the list has a scrollbar, then drag it down
    home_page.expect_hamburger_menu_is_scrollable()
    before = home_page.hamburger_scroll_metrics()["scrollTop"]
    home_page.scroll_hamburger_menu()
    after = home_page.hamburger_scroll_metrics()["scrollTop"]
    assert after > before, f"Scrollbar did not move the list: {before} -> {after}"
    home_page.expect_hamburger_menu_scrolled()

    # Step 4: Bottom of the menu (Sign in) should be in view after scrolling
    expect(home_page.page.get_by_role("dialog").get_by_text("Sign in", exact=True).first).to_be_visible()
