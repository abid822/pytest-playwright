class ElectronicsLocators:
    URL = "https://www.amazon.com/electronics-store/b?node=172282"
    # Store strip under the header: Cell Phones, Computers, TV & Video, Headphones, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Current price on a store-page product card. The struck-through price is separate.
    PRODUCT_PRICE = ".dcl-price-single .a-offscreen"
