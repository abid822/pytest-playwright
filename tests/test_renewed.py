import pytest

from pages.renewed_page import RenewedPage


@pytest.mark.desktop_only
@pytest.mark.renewed
def test_renewed_headphones_shows_a_price(renewed_page: RenewedPage):
    # Step 1: Open the Amazon Renewed store
    renewed_page.open_renewed()
    # Step 2: Core store categories are listed
    renewed_page.expect_core_categories()
