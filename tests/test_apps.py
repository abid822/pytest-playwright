import pytest

from pages.apps_page import AppsPage


@pytest.mark.desktop_only
@pytest.mark.apps
def test_apps_fire_tablet_shows_a_price(apps_page: AppsPage):
    """Opens Apps & Games, checks the store categories, and opens Fire Tablet Apps to see a price."""
    # Step 1: Open the Apps & Games store
    apps_page.open_apps()
    # Step 2: Core store categories are listed
    apps_page.expect_core_categories()
    # Step 3: Open Fire Tablet Apps
    apps_page.open_category("Fire Tablet Apps")
    # Step 4: A product on that page shows a price
    apps_page.expect_priced_product()
