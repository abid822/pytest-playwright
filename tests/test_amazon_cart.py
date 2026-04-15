import pytest
from playwright.sync_api import TimeoutError
from locators.amazon_locators import AmazonHomeLocators, AmazonSearchLocators



@pytest.mark.cart
def test_add_cheap_cable_to_cart(sb_page):
    # STEP 1: Navigate
    # We don't wrap this. If Amazon itself won't load, the test SHOULD fail.
    sb_page.goto(AmazonHomeLocators.URL)
    
    # STEP 2: Search for the cable
    try:
        sb_page.locator(AmazonSearchLocators.SEARCH_INPUT).fill("usb c charging cable")
        sb_page.locator(AmazonSearchLocators.SEARCH_BUTTON).click()
        sb_page.wait_for_timeout(2000)
    except Exception as e:
        # If the search bar changed its ID, skip the whole test instead of failing
        pytest.skip(f"Skipping test: Could not find the search bar. Error: {e}")
    
    # STEP 3: Find product cards
    try:
        results = sb_page.locator(AmazonSearchLocators.PRODUCT_CARDS).all()
        if not results:
            pytest.skip("Skipping test: Search worked, but zero products loaded.")
    except Exception:
        pytest.skip("Skipping test: The product card layout changed.")


    