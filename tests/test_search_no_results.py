import pytest

from pages.search_results_page import SearchResultsPage

# A query that does not match a product. Amazon should show the empty state.
NO_MATCH_QUERY = "zzzzqqqnonexistentitem987654"


@pytest.mark.search
def test_search_with_no_matches_shows_an_empty_state(
    search_results_page: SearchResultsPage,
):
    """Searches for a query that matches nothing and checks the empty-state message."""
    # Step 1: Search for a query that should not match a product
    search_results_page.search_with_no_results(NO_MATCH_QUERY)
    # Step 2: The empty-state message is shown and no product cards are listed
    search_results_page.expect_no_results()
