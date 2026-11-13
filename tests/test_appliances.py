import pytest

from pages.appliances_page import AppliancesPage


@pytest.mark.desktop_only
@pytest.mark.appliances
def test_appliances_refrigeration_shows_a_price(appliances_page: AppliancesPage):
    """Opens Appliances, checks the store categories, and opens Refrigeration to see a price."""
    # Step 1: Open the Appliances store
    appliances_page.open_appliances()
    # Step 2: Core store categories are listed
    appliances_page.expect_core_categories()
    # Step 3: Open Refrigeration
    appliances_page.open_category("Refrigeration")
    # Step 4: A product on that page shows a price
    appliances_page.expect_priced_product()
