class AppliancesLocators:
    URL = "https://www.amazon.com/appliances/b?node=2619525011"
    # Store strip under the header: Refrigeration, Cooking, Dishwashers, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
