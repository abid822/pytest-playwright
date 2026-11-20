class MoviesTvLocators:
    URL = "https://www.amazon.com/movies-tv-dvd-bluray/b?node=2625373011"
    # Store strip under the header: Movies, TV shows, Blu-ray, 4K Store, ...
    SUBNAV = "#nav-subnav"
    SUBNAV_LINK = "#nav-subnav a.nav-a"
    # Screen-reader price on a category-page product card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
