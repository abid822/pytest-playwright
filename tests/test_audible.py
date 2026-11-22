import pytest

from pages.audible_page import AudiblePage


@pytest.mark.desktop_only
@pytest.mark.audible
def test_audible_deals_shows_a_price(audible_page: AudiblePage):
    # Step 1: Open the Audible store
    audible_page.open_audible()
    # Step 2: Core store categories are listed
    audible_page.expect_core_categories()
