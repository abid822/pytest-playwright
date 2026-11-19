import pytest

from pages.clothing_page import ClothingPage


@pytest.mark.desktop_only
@pytest.mark.clothing
def test_clothing_luggage_shows_a_price(clothing_page: ClothingPage):
    """Opens Clothing, Shoes & Jewelry, checks the store categories, and opens Luggage to see a price."""
    # Step 1: Open the Clothing, Shoes & Jewelry store
    clothing_page.open_clothing()
    # Step 2: Core store categories are listed
    clothing_page.expect_core_categories()
    # Step 3: Open Luggage
    clothing_page.open_category("Luggage")
    # Step 4: A product on that page shows a price
    clothing_page.expect_priced_product()
