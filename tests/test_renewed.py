import pytest

from pages.renewed_page import RenewedPage


@pytest.mark.desktop_only
@pytest.mark.renewed
def test_renewed_product_shows_a_price(renewed_page: RenewedPage):
    """Opens Amazon Renewed, checks the store sections, and checks that a refurbished product shows a price."""
    # Step 1: Open the Amazon Renewed store
    renewed_page.open_renewed()
    # Step 2: Core store sections are listed
    renewed_page.expect_core_sections()
    # Step 3: A refurbished product shows a price
    renewed_page.expect_priced_product()
