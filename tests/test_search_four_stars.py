import pytest

from pages.search_results_page import SearchResultsPage

# A common product search. The left nav offers a 4 Stars & Up refinement.
FOUR_STAR_QUERY = "stainless steel water bottle"


@pytest.mark.desktop_only
@pytest.mark.search
def test_search_four_stars_and_up_keeps_highly_rated_results(
    search_results_page: SearchResultsPage,
):
    """Searches for a water bottle, applies 4 Stars & Up, and checks the filter stays selected with ratings of 4 or higher."""
    # Step 1: Search for a product that has a customer-review filter
    search_results_page.search_from_home(FOUR_STAR_QUERY)
    # Step 2: Apply the 4 Stars & Up refinement
    search_results_page.filter_by_four_stars_and_up()
    # Step 3: The filter stays selected and the listed ratings are 4 or higher
    search_results_page.expect_four_star_results()
