import pytest

from pages.handmade_page import HandmadePage


@pytest.mark.desktop_only
@pytest.mark.handmade
def test_handmade_jewelry_shows_a_price(handmade_page: HandmadePage):
    """Opens Handmade, checks the shop categories, and opens Jewelry to see a price."""
    # Step 1: Open the Handmade store
    handmade_page.open_handmade()
    # Step 2: Core shop categories are listed
    handmade_page.expect_core_categories()
    # Step 3: Open Jewelry
    handmade_page.open_category("Jewelry")
    # Step 4: A product on that page shows a price
    handmade_page.expect_priced_product()
