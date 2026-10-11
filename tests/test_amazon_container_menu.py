import json
from pathlib import Path

import pytest


@pytest.mark.tabs
@pytest.mark.smoke
def test_amazon_container_menu(home_page):
    home_page.open_home()
    home_page.open_hamburger_menu()

    data_file = Path(__file__).parent.parent / "data" / "hamburger_menu.json"
    expected = json.loads(data_file.read_text())
    home_page.expect_menu_contains(expected)
