class GiftCardsLocators:
    URL = "https://www.amazon.com/gift-cards/b/?ie=UTF8&node=2238192011"
    # Gift Cards subnav under the store tab
    REDEEM_LINK = "a[href*='/gc/redeem']"
    BALANCE_LINK = "a[href*='/gp/css/gc/balance']"
    # One card in a shop-by carousel
    PRODUCT_LINK = "a.dcl-product-link"
    # Detail page for a single eGift card
    PRODUCT_TITLE = "span#productTitle"  # visible title; a hidden input shares the id
    PRICE = "#corePrice_feature_div .a-offscreen"
