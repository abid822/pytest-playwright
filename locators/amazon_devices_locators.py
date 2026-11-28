class AmazonDevicesLocators:
    URL = "https://www.amazon.com/Amazon-Devices/b?node=2102313011"
    # "Shop Kindle" under the Kindle section. The header strip is hidden.
    KINDLE_SHOP_LINK = "a[href*='kindle/shop']"
    # Screen-reader price on a Kindle e-reader card.
    PRODUCT_PRICE = ".a-price .a-offscreen"
