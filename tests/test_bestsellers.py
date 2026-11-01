import pytest

from pages.bestsellers_page import BestSellersPage


@pytest.mark.desktop_only
@pytest.mark.bestsellers
def test_best_sellers_electronics_shows_number_one(
    bestsellers_page: BestSellersPage,
):
    """Opens Best Sellers, checks core departments, and opens Electronics to see the #1 product."""
    # Step 1: Open the Best Sellers page
    bestsellers_page.open_best_sellers()
    # Step 2: Core departments are listed
    bestsellers_page.expect_core_departments()
    # Step 3: Open Electronics
    bestsellers_page.open_department("Electronics")
    # Step 4: The list has a ranked #1 product
    bestsellers_page.expect_number_one_product()
