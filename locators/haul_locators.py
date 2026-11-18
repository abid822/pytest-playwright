class HaulLocators:
    URL = "https://www.amazon.com/haul/store"
    # Store strip under the header: Deals, Women, Men, Kids, Home, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a Haul product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
    # Search-result card after a Haul category opens.
    RESULTS = "div[data-component-type='s-search-result']"
