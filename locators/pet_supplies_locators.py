class PetSuppliesLocators:
    URL = "https://www.amazon.com/pet-supplies/b?node=2619533011"
    # Store strip under the header: Dogs, Cats, Fish & Aquatics, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
