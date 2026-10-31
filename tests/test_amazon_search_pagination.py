import pytest

from pages.search_results_page import SearchResultsPage


@pytest.mark.search
def test_search_results_second_page_lists_different_products(
    search_results_page: SearchResultsPage,
):
    # Step 1: Search for a query that has more than one page of results
    search_results_page.search_from_home("hardcover notebook")
    # Step 2: Remember the first organic titles on page 1
    page_one_titles = search_results_page.organic_result_titles()
    # Step 3: Open page 2 from the pagination strip
    search_results_page.go_to_results_page(2)
    # Step 4: Page 2 should show a different set of products
    page_two_titles = search_results_page.organic_result_titles()
    assert page_two_titles != page_one_titles, (
        f"Page 2 repeated page 1 results: {page_two_titles}"
    )
