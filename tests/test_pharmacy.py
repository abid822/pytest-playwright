import pytest

from pages.pharmacy_page import PharmacyPage


@pytest.mark.pharmacy
def test_pharmacy_rxpass_shows_a_monthly_price(pharmacy_page: PharmacyPage):
    """Opens Amazon Pharmacy, checks the pharmacy sections, and opens RxPass to see the monthly price."""
    # Step 1: Open Amazon Pharmacy
    pharmacy_page.open_pharmacy()
    # Step 2: How it works, PillPack, RxPass, and the medication search are listed
    pharmacy_page.expect_core_sections()
    # Step 3: Open RxPass
    pharmacy_page.open_rxpass()
    # Step 4: RxPass shows a monthly price
    pharmacy_page.expect_monthly_price()
