class AmazonHomeLocators:
    URL = "https://www.amazon.com/"


class AmazonSearchLocators:
    SEARCH_INPUT = "#twotabsearchtextbox"  # header search box
    SEARCH_BUTTON = "#nav-search-submit-button"  # magnifying-glass submit
    PRODUCT_CARDS = "div[data-component-type='s-search-result']"  # one result row
    PRICE_WHOLE = ".a-price-whole"
    ADD_TO_CART_BUTTON = "button:has-text('Add to cart')"
    SORT_SELECT = "#s-result-sort-select"  # Featured / Price: Low to High
