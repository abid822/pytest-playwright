class AmazonHomeLocators:
    URL = "https://www.amazon.com/home-garden-kitchen-furniture-bedding/b?node=1055398"
    # Store strip under the header: Shop by Room, Furniture, Kitchen & Dining, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Current price on a store-page product card. The struck-through price is separate.
    PRODUCT_PRICE = ".dcl-price-single .a-offscreen"
