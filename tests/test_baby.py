import pytest

from pages.baby_page import BabyPage


@pytest.mark.desktop_only
@pytest.mark.baby
def test_baby_strollers_shows_a_price(baby_page: BabyPage):
    """Opens Baby, checks the store categories, and opens Strollers to see a price."""
    # Step 1: Open the Baby store
    baby_page.open_baby()
    # Step 2: Core store categories are listed
    baby_page.expect_core_categories()
    # Step 3: Open Strollers
    baby_page.open_category("Strollers")
    # Step 4: A product on that page shows a price
    baby_page.expect_priced_product()
