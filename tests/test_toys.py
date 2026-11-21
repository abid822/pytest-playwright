import pytest

from pages.toys_page import ToysPage


@pytest.mark.desktop_only
@pytest.mark.toys
def test_toys_character_store_shows_a_price(toys_page: ToysPage):
    """Opens Toys & Games, checks the store categories, and opens Shop Toys by Character to see a price."""
    # Step 1: Open the Toys & Games store
    toys_page.open_toys()
    # Step 2: Core store categories are listed
    toys_page.expect_core_categories()
    # Step 3: Open Shop Toys by Character
    toys_page.open_category("Shop Toys by Character")
    # Step 4: A product on that page shows a price
    toys_page.expect_priced_product()
