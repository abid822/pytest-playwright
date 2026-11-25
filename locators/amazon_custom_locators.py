class AmazonCustomLocators:
    URL = "https://www.amazon.com/b?node=11032013011"
    # Store strip under the header: Kitchen, Jewelry, Pets, Home, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
