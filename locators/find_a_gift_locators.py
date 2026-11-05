class FindAGiftLocators:
    URL = "https://www.amazon.com/b?node=206764924011"
    # Occasion tile. Birthdays opens a list of gifts.
    OCCASION_LINK = "a.a-link-normal"
    # One product tile on the birthday list
    RESULT = "[data-cy='asin-faceout-container']"
    PRODUCT_TITLE = "h2"
    PRICE = ".a-price .a-offscreen"
