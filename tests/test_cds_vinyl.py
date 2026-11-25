import pytest

from pages.cds_vinyl_page import CDsVinylPage


@pytest.mark.desktop_only
@pytest.mark.cds_vinyl
def test_cds_vinyl_rock_shows_a_price(cds_vinyl_page: CDsVinylPage):
    """Opens CDs & Vinyl, checks the store genres, and opens Rock to see a price."""
    # Step 1: Open the CDs & Vinyl store
    cds_vinyl_page.open_cds_vinyl()
    # Step 2: Core store genres are listed
    cds_vinyl_page.expect_core_genres()
    # Step 3: Open Rock
    cds_vinyl_page.open_genre("Rock")
    # Step 4: An album on that page shows a price
    cds_vinyl_page.expect_priced_product()
