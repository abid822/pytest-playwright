import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@pytest.mark.cart
@pytest.mark.smoke
def test_add_cheap_cable_to_cart(home_page: HomePage, search_results_page: SearchResultsPage):
    # Step 1: Open Amazon home
    home_page.open_home()
    # Step 2: Search for a cheap cable
    home_page.search("usb c charging cable")
    # Step 3: Add the first result to the cart
    search_results_page.add_first_result_to_cart()
    # Step 4: Cart badge should no longer be 0
    home_page.expect_cart_not_empty()
