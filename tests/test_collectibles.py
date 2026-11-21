import pytest

from pages.collectibles_page import CollectiblesPage


@pytest.mark.desktop_only
@pytest.mark.collectibles
def test_collectibles_coins_shows_a_price(collectibles_page: CollectiblesPage):
    """Opens Collectibles & Fine Art, checks the store categories, and opens Collectible Coins to see a price."""
    # Step 1: Open the Collectibles & Fine Art store
    collectibles_page.open_collectibles()
    # Step 2: Core store categories are listed
    collectibles_page.expect_core_categories()
    # Step 3: Open Collectible Coins
    collectibles_page.open_category("Collectible Coins")
    # Step 4: A product on that page shows a price
    collectibles_page.expect_priced_product()
