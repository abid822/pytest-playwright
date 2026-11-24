class PrimeVideoLocators:
    URL = "https://www.amazon.com/gp/video/storefront"
    # Row heading on the storefront. The row names rotate.
    CAROUSEL_TITLE = "[data-testid='carousel-title']"
    # A movie or show card. The title itself rotates.
    TITLE_LINK = "a[href*='/gp/video/detail']"
