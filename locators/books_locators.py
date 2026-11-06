class BooksLocators:
    URL = "https://www.amazon.com/books-used-books-textbooks/b?ie=UTF8&node=283155"
    # Genre tiles under Explore top categories. Seasonal rows below them rotate.
    GENRE_LIST = "[data-testid='explore-genres.container']"
    GENRE_LINK = "bds-link[data-testid^='explore-genres.link']"
    # One book card on a Books category page.
    BOOK = "bds-unified-book-faceout"
    BOOK_TITLE = "a.cover-image-link"
    BOOK_PRICE = "bds-book-price"
