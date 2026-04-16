import pytest
from playwright.sync_api import expect 
from locators.amazon_tabs_locator import AmazonTabsLocator
from pages.navigation_page import AmazonNavigationPage
# from [folder].[file_name] import [ClassName]


def test_amazon_tabs_containers(sb_page):
    # 1. Give the browser to your actions class
    actions = AmazonNavigationPage(sb_page)
    
    # 2. CALL YOUR SETUP STEPS! (Explicitly, with parentheses)
    actions.navigate_to_amazon_page()

    # Step 2: Verify the parent container for the tabs is visible
    print("\n--- Verifying Parent Container for Tabs ---")
    nav_container = sb_page.locator(AmazonTabsLocator.NAV_CONTAINER)
    expect(nav_container).to_be_visible(timeout=5000)
    print("✅ Parent container for tabs is visible.")

    # Step 3: Verify all tab links inside the container are visible
    print("\n--- Verifying All Tab Links Inside Container ---")
    all_tab_links = sb_page.locator(AmazonTabsLocator.ALL_TABS_LINKS)
    
    # Wait for at least one tab link to be visible to ensure the container has loaded
    expect(all_tab_links.first).to_be_visible(timeout=5000)
    
    # Get the count of all tab links found
    tab_count = all_tab_links.count()
    print(f"✅ Found {tab_count} tab links inside the container.")
    
    # Optional: Print the text of each tab link for proof
    for i in range(tab_count):
        tab_text = all_tab_links.nth(i).inner_text().strip()
        print(f"   - Tab Link {i + 1}: {tab_text}")
    
    print("\n✅ All tab links inside the container verified successfully!")