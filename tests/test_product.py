import pytest

from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage

# A common household product. The first organic result has a standard detail page.
PRODUCT_QUERY = "aaa batteries"


@pytest.mark.desktop_only
@pytest.mark.product
def test_search_result_shows_title_price_and_add_to_cart(
    search_results_page: SearchResultsPage,
    product_page: ProductPage,
):
    """Searches for batteries, opens the first result, and checks the title, price, and Add to cart."""
    # Step 1: Search for a product that has a detail page
    search_results_page.search_from_home(PRODUCT_QUERY)
    # Step 2: Open the first organic result
    product_page.open_first_result()
    # Step 3: The product page shows a title, a price, and Add to cart
    product_page.expect_title_price_and_add_to_cart()
