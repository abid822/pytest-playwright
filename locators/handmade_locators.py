class HandmadeLocators:
    URL = "https://www.amazon.com/gp/browse.html?node=120955898011"
    # "Explore the Handmade Shop" sits above the department tiles.
    SHOP_HEADING = "h2.dcl-header-title"
    # Department tiles. The top nav repeats some of the same words.
    CATEGORY_LINK = "a[href*='i=handmade']"
    # Screen-reader price on a Handmade search result.
    PRODUCT_PRICE = ".a-price .a-offscreen"
