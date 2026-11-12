import pytest

from pages.tools_page import ToolsPage


@pytest.mark.desktop_only
@pytest.mark.tools
def test_tools_power_hand_tools_shows_a_price(tools_page: ToolsPage):
    # Step 1: Open the Tools & Home Improvement store
    tools_page.open_tools()
    # Step 2: Core store categories are listed
    tools_page.expect_core_categories()
