class BabyLocators:
    URL = "https://www.amazon.com/baby-products/b?node=165796011"
    # Store strip under the header: Strollers, Car Seats, Nursery, Feeding, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Current price on a store-page product card. The struck-through price is separate.
    PRODUCT_PRICE = ".dcl-price-single .a-offscreen"
