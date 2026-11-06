import pytest

from pages.books_page import BooksPage


@pytest.mark.books
def test_books_literature_shows_a_price(books_page: BooksPage):
    """Opens Books, checks the store sections, and opens Literature & Fiction to see a book with a price."""
    # Step 1: Open the Books store
    books_page.open_books()
    # Step 2: Reading, discover, and category sections are listed
    books_page.expect_shop_sections()
    # Step 3: Romance, Children's Books, and the other core categories are offered
    books_page.expect_categories()
    # Step 4: Open Literature & Fiction
    books_page.open_category("Literature & Fiction")
    # Step 5: A book has a title and a price
    books_page.expect_priced_book()
