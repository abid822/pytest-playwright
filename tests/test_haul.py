import pytest

from pages.haul_page import HaulPage


@pytest.mark.desktop_only
@pytest.mark.haul
def test_haul_women_shows_a_price(haul_page: HaulPage):
    """Opens Amazon Haul, checks the store categories, and opens Women to see a price."""
    # Step 1: Open the Amazon Haul store
    haul_page.open_haul()
    # Step 2: Core store categories are listed
    haul_page.expect_core_categories()
    # Step 3: Open Women
    haul_page.open_category("Women")
    # Step 4: A product on that page shows a price
    haul_page.expect_priced_product()
