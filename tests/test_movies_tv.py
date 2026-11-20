import pytest

from pages.movies_tv_page import MoviesTvPage


@pytest.mark.desktop_only
@pytest.mark.movies_tv
def test_movies_tv_bluray_shows_a_price(movies_tv_page: MoviesTvPage):
    # Step 1: Open the Movies & TV store
    movies_tv_page.open_movies_tv()
    # Step 2: Core store categories are listed
    movies_tv_page.expect_core_categories()
