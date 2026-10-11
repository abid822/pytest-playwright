import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@pytest.mark.cart
@pytest.mark.smoke
def test_add_cheap_cable_to_cart(home_page: HomePage, search_results_page: SearchResultsPage):
    home_page.open_home()
    home_page.search("usb c charging cable")
    search_results_page.add_first_result_to_cart()
    home_page.expect_cart_not_empty()
