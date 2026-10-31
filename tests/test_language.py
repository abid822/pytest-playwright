import pytest

from pages.home_page import HomePage


@pytest.mark.language
def test_language_settings_keep_english_and_offer_spanish(home_page: HomePage):
    # Step 1: Open Amazon home
    home_page.open_home()
    # Step 2: Open language preferences from the header EN control
    home_page.open_language_settings()
    # Step 3: English stays selected, Spanish is offered, and nothing is saved
    home_page.expect_english_selected_and_spanish_available()
