import pytest
from playwright.sync_api import expect 
from locators.amazon_tabs_locator import AmazonTabsLocator
from pages.navigation_page import AmazonNavigationPage
# from [folder].[file_name] import [ClassName]



@pytest.mark.smoke
def test_amazon_tabs(sb_page):
    # 1. Give the browser to your actions class
    actions = AmazonNavigationPage(sb_page)
    
    # 2. CALL YOUR SETUP STEPS! (Explicitly, with parentheses)
    actions.navigate_to_amazon_page()

 # Step 2: Define the list of tabs we expect to see
    expected_tabs = [
        AmazonTabsLocator.AMAZON_HAUL,
        AmazonTabsLocator.MEDICAL_CARE,
        AmazonTabsLocator.AMAZON_BASICS,
        AmazonTabsLocator.BEST_SELLERS,
        AmazonTabsLocator.BOOKS,
        AmazonTabsLocator.TODAYS_DEALS,
        AmazonTabsLocator.PRIME,
        AmazonTabsLocator.GIFT_CARDS,
        AmazonTabsLocator.SELL,
        AmazonTabsLocator.GROCERIES,
        AmazonTabsLocator.NEW_RELEASES,
        AmazonTabsLocator.REGISTRY
    ]

    # Step 3: Loop and verify
    print("\n--- Verifying Navigation Tabs ---")
    for tab in expected_tabs:
        element = sb_page.locator(tab)
        
        # This will wait for the tab to appear and fail if it's missing
        expect(element).to_be_visible(timeout=5000)
        
        # Optional: Print the text of the tab to your console for proof
        print(f"✅ Found Tab: {element.inner_text().strip()}")

    # Step 3: Loop through the list and assert each tab is visible
    print("\n--- Step 3: Asserting tabs are visible ---")
    for locator_string in expected_tabs:
        # Create the Playwright element from the string
        tab_element = sb_page.locator(locator_string)
        
        # Assert it is visible on the screen
        expect(tab_element).to_be_visible()
        
        # Log success for the terminal output
        print(f"✅ Verified tab is visible: {locator_string}")
        
    print("\n✅ All navigation tabs verified successfully!")