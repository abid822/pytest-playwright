class RenewedLocators:
    URL = "https://www.amazon.com/Amazon-Renewed/b?node=12653393011"
    # Category tiles that stay in the Renewed store. The main nav is a different set.
    CATEGORY_LINK = "a[href*='srs=12653393011']"
    # Search box scope once a Renewed category is open.
    SEARCH_SCOPE = "#nav-search-label-id"
    # A product card on the category page, and the title inside it.
    RESULT_CARD = "[data-component-type='s-search-result']"
    RESULT_TITLE = "h2"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
