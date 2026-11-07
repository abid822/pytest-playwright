import pytest

from pages.beauty_page import BeautyPage


@pytest.mark.desktop_only
@pytest.mark.beauty
def test_beauty_makeup_shows_a_price(beauty_page: BeautyPage):
    """Opens Beauty, checks the store categories, and opens Makeup to see a price."""
    # Step 1: Open the Beauty store
    beauty_page.open_beauty()
    # Step 2: Core store categories are listed
    beauty_page.expect_core_categories()
    # Step 3: Open Makeup
    beauty_page.open_category("Makeup")
    # Step 4: A product on that page shows a price
    beauty_page.expect_priced_product()
