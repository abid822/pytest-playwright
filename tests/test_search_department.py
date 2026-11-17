import pytest

from pages.search_results_page import SearchResultsPage

# A book query. The header department list can scope it to Books.
BOOK_QUERY = "python"


@pytest.mark.desktop_only
@pytest.mark.search
def test_search_books_department_keeps_book_results(
    search_results_page: SearchResultsPage,
):
    """Opens the header department list, checks the core departments, and searches Books so the results stay in Books."""
    # Step 1: Open Amazon home and the department list
    search_results_page.open_search_departments()
    # Step 2: Core departments are listed
    search_results_page.expect_core_search_departments()
    # Step 3: Search inside Books
    search_results_page.search_in_department("Books", BOOK_QUERY)
    # Step 4: The department stays on Books and results are listed
    search_results_page.expect_department_results("Books", BOOK_QUERY)
