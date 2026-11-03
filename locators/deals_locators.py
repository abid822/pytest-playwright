class DealsLocators:
    URL = "https://www.amazon.com/deals"
    PRODUCT_CARD = "[data-testid='product-card']"  # one deal tile
    PRODUCT_LINK = "[data-testid='product-card-link']"  # title or discount badge
    # Desktop prefix is filter-bubble-. Mobile web prefix is bubble-.
    FILTER_BUBBLE = "[data-testid='filter-bubble-{suffix}'], [data-testid='bubble-{suffix}']"
