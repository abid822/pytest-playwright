import pytest

from pages.audible_page import AudiblePage


@pytest.mark.desktop_only
@pytest.mark.audible
def test_audible_deals_shows_a_price(audible_page: AudiblePage):
    """Opens Audible Books & Originals, checks the store categories, and opens Audiobook Deals to see a price."""
    # Step 1: Open the Audible store
    audible_page.open_audible()
    # Step 2: Core store categories are listed
    audible_page.expect_core_categories()
    # Step 3: Open Audiobook Deals
    audible_page.open_category("Audiobook Deals")
    # Step 4: A title on that page shows a price
    audible_page.expect_priced_product()
