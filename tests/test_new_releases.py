import pytest

from pages.new_releases_page import NewReleasesPage


@pytest.mark.desktop_only
@pytest.mark.new_releases
def test_new_releases_electronics_shows_number_one(
    new_releases_page: NewReleasesPage,
):
    """Opens New Releases, checks core departments, and opens Electronics to see the #1 product."""
    # Step 1: Open the New Releases page
    new_releases_page.open_new_releases()
    # Step 2: Core departments are listed
    new_releases_page.expect_core_departments()
    # Step 3: Open Electronics
    new_releases_page.open_department("Electronics")
    # Step 4: The list has a ranked #1 product
    new_releases_page.expect_number_one_product()
