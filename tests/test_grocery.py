import pytest

from pages.grocery_page import GroceryPage


@pytest.mark.desktop_only
@pytest.mark.grocery
def test_grocery_product_shows_a_price(grocery_page: GroceryPage):
    """Opens Grocery, checks the store aisles, and checks that a product shows a price."""
    # Step 1: Open the Grocery store
    grocery_page.open_grocery()
    # Step 2: Core store aisles are listed
    grocery_page.expect_core_aisles()
    # Step 3: Breakfast is one of those aisle cards
    grocery_page.expect_breakfast_aisle()
    # Step 4: A product on the Grocery page shows a price
    grocery_page.expect_priced_product()
