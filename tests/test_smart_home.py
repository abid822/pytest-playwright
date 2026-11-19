import pytest

from pages.smart_home_page import SmartHomePage


@pytest.mark.desktop_only
@pytest.mark.smart_home
def test_smart_home_cameras_shows_a_price(smart_home_page: SmartHomePage):
    """Opens Smart Home, checks the store categories, and opens Cameras to see a price."""
    # Step 1: Open the Smart Home store
    smart_home_page.open_smart_home()
    # Step 2: Core store categories are listed
    smart_home_page.expect_core_categories()
    # Step 3: Open Cameras
    smart_home_page.open_category("Cameras")
    # Step 4: A product on that page shows a price
    smart_home_page.expect_priced_product()
