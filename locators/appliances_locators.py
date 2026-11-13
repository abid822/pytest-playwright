class AppliancesLocators:
    URL = "https://www.amazon.com/home-appliances/b?node=2619525011"
    # Store strip under the header: Refrigeration, Cooking, Washers & Dryers, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
