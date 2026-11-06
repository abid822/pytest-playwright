import pytest

from pages.amazon_home_page import AmazonHomePage


@pytest.mark.desktop_only
@pytest.mark.amazon_home
def test_amazon_home_kitchen_shows_a_price(amazon_home_page: AmazonHomePage):
    """Opens Amazon Home, checks the store categories, and opens Kitchen & Dining to see a price."""
    # Step 1: Open the Amazon Home store
    amazon_home_page.open_amazon_home()
    # Step 2: Core store categories are listed
    amazon_home_page.expect_core_categories()
    # Step 3: Open Kitchen & Dining
    amazon_home_page.open_category("Kitchen & Dining")
    # Step 4: A product on that page shows a price
    amazon_home_page.expect_priced_product()
