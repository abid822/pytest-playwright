import pytest

from pages.amazon_custom_page import AmazonCustomPage


@pytest.mark.desktop_only
@pytest.mark.amazon_custom
def test_amazon_custom_jewelry_shows_a_price(amazon_custom_page: AmazonCustomPage):
    """Opens Amazon Custom, checks the store categories, and opens Jewelry to see a price."""
    # Step 1: Open the Amazon Custom store
    amazon_custom_page.open_amazon_custom()
    # Step 2: Core store categories are listed
    amazon_custom_page.expect_core_categories()
    # Step 3: Open Jewelry
    amazon_custom_page.open_category("Jewelry")
    # Step 4: A product on that page shows a price
    amazon_custom_page.expect_priced_product()
