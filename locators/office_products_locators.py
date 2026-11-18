class OfficeProductsLocators:
    URL = "https://www.amazon.com/office-products/b?node=1064954"
    # Store strip under the header: Office Deals, School Supplies, Printers, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
