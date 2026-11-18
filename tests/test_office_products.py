import pytest

from pages.office_products_page import OfficeProductsPage


@pytest.mark.desktop_only
@pytest.mark.office_products
def test_office_products_school_supplies_shows_a_price(
    office_products_page: OfficeProductsPage,
):
    """Opens Office Products, checks the store categories, and opens School Supplies to see a price."""
    # Step 1: Open the Office Products store
    office_products_page.open_office_products()
    # Step 2: Core store categories are listed
    office_products_page.expect_core_categories()
    # Step 3: Open School Supplies
    office_products_page.open_category("School Supplies")
    # Step 4: A product on that page shows a price
    office_products_page.expect_priced_product()
