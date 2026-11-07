import pytest

from pages.electronics_page import ElectronicsPage


@pytest.mark.desktop_only
@pytest.mark.electronics
def test_electronics_headphones_shows_a_price(electronics_page: ElectronicsPage):
    """Opens Electronics, checks the store categories, and opens Headphones to see a price."""
    # Step 1: Open the Electronics store
    electronics_page.open_electronics()
    # Step 2: Core store categories are listed
    electronics_page.expect_core_categories()
    # Step 3: Open Headphones
    electronics_page.open_category("Headphones")
    # Step 4: A product on that page shows a price
    electronics_page.expect_priced_product()
