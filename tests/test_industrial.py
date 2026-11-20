import pytest

from pages.industrial_page import IndustrialPage


@pytest.mark.desktop_only
@pytest.mark.industrial
def test_industrial_food_service_shows_a_price(industrial_page: IndustrialPage):
    """Opens Industrial & Scientific, checks the store categories, and opens Food Service to see a price."""
    # Step 1: Open the Industrial & Scientific store
    industrial_page.open_industrial()
    # Step 2: Core store categories are listed
    industrial_page.expect_core_categories()
    # Step 3: Open Food Service
    industrial_page.open_category("Food Service")
    # Step 4: A product on that page shows a price
    industrial_page.expect_priced_product()
