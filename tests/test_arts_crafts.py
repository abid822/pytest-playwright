import pytest

from pages.arts_crafts_page import ArtsCraftsPage


@pytest.mark.desktop_only
@pytest.mark.arts_crafts
def test_arts_crafts_fabric_shows_a_price(arts_crafts_page: ArtsCraftsPage):
    """Opens Arts, Crafts & Sewing, checks the store categories, and opens Fabric to see a price."""
    # Step 1: Open the Arts, Crafts & Sewing store
    arts_crafts_page.open_arts_crafts()
    # Step 2: Core store categories are listed
    arts_crafts_page.expect_core_categories()
    # Step 3: Open Fabric
    arts_crafts_page.open_category("Fabric")
    # Step 4: A product on that page shows a price
    arts_crafts_page.expect_priced_product()
