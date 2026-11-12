class ProductLocators:
    # Title link on a search card. The anchor wraps the heading.
    RESULT_LINK = "a[href*='/dp/']"
    TITLE = "#productTitle"
    # Current price in the desktop buy box. The unit price is a later node.
    PRICE = (
        "#corePrice_feature_div .a-offscreen, "
        "#corePriceDisplay_desktop_feature_div .priceToPay .a-offscreen"
    )
    ADD_TO_CART = "#add-to-cart-button"
