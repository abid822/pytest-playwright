class BeautyLocators:
    URL = "https://www.amazon.com/Beauty/b?node=3760911"
    # Store strip under the header: Makeup, Skin Care, Hair Care, Fragrance, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Current price on a store-page product card. The struck-through price is separate.
    PRODUCT_PRICE = ".dcl-price-single .a-offscreen"
