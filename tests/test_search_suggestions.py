import pytest

from pages.search_results_page import SearchResultsPage

# A short prefix. Amazon's dropdown offers several keywords that start with it.
SUGGESTION_PREFIX = "wireless"


@pytest.mark.desktop_only
@pytest.mark.search
def test_search_suggestions_open_a_matching_result(
    search_results_page: SearchResultsPage,
):
    """Types a search prefix, checks the suggestion list, and opens one suggestion."""
    # Step 1: Type a prefix in the search box
    search_results_page.type_search_prefix(SUGGESTION_PREFIX)
    # Step 2: The dropdown lists suggestions that include that prefix
    search_results_page.expect_search_suggestions(SUGGESTION_PREFIX)
    # Step 3: Open the first matching suggestion
    search_results_page.open_matching_suggestion(SUGGESTION_PREFIX)
