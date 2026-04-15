class AmazonHomeLocators:
    URL = "https://www.amazon.com/"

class AmazonSearchLocators:
    SEARCH_INPUT = "#twotabsearchtextbox"
    SEARCH_BUTTON = "#nav-search-submit-button"

    #Sort by less then $10
    UP_TO_10_FILTER = "span:has-text('Up to $10')"
    
    # This finds the 'container' for each product result
    PRODUCT_CARDS = "div[data-component-type='s-search-result']"
    
    # These are nested inside the product cards
    PRICE_WHOLE = ".a-price-whole"
    # This button often changes; this is the most reliable way to find it
    ADD_TO_CART_BUTTON = "button:has-text('Add to cart')"