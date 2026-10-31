class AmazonHomeLocators:
    URL = "https://www.amazon.com/"
    # Bot check Amazon shows before the storefront on a fresh session
    CONTINUE_SHOPPING_BUTTON = "form[action*='validateCaptcha'] button"


class AmazonSearchLocators:
    SEARCH_INPUT = "#twotabsearchtextbox"  # header search box
    SEARCH_BUTTON = "#nav-search-submit-button"  # magnifying-glass submit
    PRODUCT_CARDS = "div[data-component-type='s-search-result']"  # one result row
    PRICE_WHOLE = ".a-price-whole"
    ADD_TO_CART_BUTTON = "button:has-text('Add to cart')"
    SORT_SELECT = "#s-result-sort-select"  # Featured / Price: Low to High
    RESULT_TITLE = "h2"  # product title inside a result card
    # aria-label is "Go to page 2", "Go to page 3", ...
    PAGINATION_PAGE_LINK = "a.s-pagination-item[aria-label='Go to page {}']"
    PAGINATION_SELECTED = "span.s-pagination-selected"  # current page number
