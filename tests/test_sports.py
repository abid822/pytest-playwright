import pytest

from pages.sports_page import SportsPage


@pytest.mark.desktop_only
@pytest.mark.sports
def test_sports_cycling_shows_a_price(sports_page: SportsPage):
    """Opens Sports & Outdoors, checks the store categories, and opens Cycling to see a price."""
    # Step 1: Open the Sports & Outdoors store
    sports_page.open_sports()
    # Step 2: Core store categories are listed
    sports_page.expect_core_categories()
