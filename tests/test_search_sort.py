import pytest

from pages.search_results_page import SearchResultsPage

# A common product with many priced results so Low to High can be checked.
SORT_QUERY = "coffee mug"


@pytest.mark.desktop_only
@pytest.mark.search
def test_search_results_sort_price_low_to_high(
    search_results_page: SearchResultsPage,
):
    """Searches for a coffee mug, sorts Price: Low to High, and checks the first prices rise."""
    # Step 1: Search for a common product
    search_results_page.search_for_sort(SORT_QUERY)
    # Step 2: Sort the results by Price: Low to High
    search_results_page.choose_price_low_to_high()
    # Step 3: The sort stays selected and the first prices are low to high
    search_results_page.expect_price_low_to_high()
