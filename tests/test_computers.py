import pytest

from pages.computers_page import ComputersPage


@pytest.mark.desktop_only
@pytest.mark.computers
def test_computers_laptops_shows_a_price(computers_page: ComputersPage):
    """Opens Computers, checks the store categories, and opens Laptops to see a price."""
    # Step 1: Open the Computers store
    computers_page.open_computers()
    # Step 2: Core store categories are listed
    computers_page.expect_core_categories()
    # Step 3: Open Laptops
    computers_page.open_category("Laptops")
    # Step 4: A product on that page shows a price
    computers_page.expect_priced_product()
