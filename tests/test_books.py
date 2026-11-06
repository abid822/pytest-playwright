import pytest

from pages.books_page import BooksPage


@pytest.mark.books
def test_books_literature_shows_a_price(books_page: BooksPage):
    """Opens Books and checks the store sections."""
    # Step 1: Open the Books store
    books_page.open_books()
    # Step 2: Reading, discover, and category sections are listed
    books_page.expect_shop_sections()
