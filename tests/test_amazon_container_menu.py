import pytest
import json
from pathlib import Path
from playwright.sync_api import expect 
from locators.amazon_tabs_locator import AmazonTabsLocator
from pages.navigation_page import AmazonNavigationPage
# from [folder].[file_name] import [ClassName]

@pytest.mark.tabs
@pytest.mark.smoke
def test_amazon_container_menu(page):
    # 1. Give the browser to your actions class
    actions = AmazonNavigationPage(page)
    
    # 2. CALL YOUR SETUP STEPS! (Explicitly, with parentheses)
    actions.navigate_to_amazon_page()

    # Step 1: Click the hamburger menu to open it
    print("\n--- Opening Hamburger Menu ---")
    page.click(AmazonTabsLocator.HAMBURGER_MENU)
    
    # Step 2: Verify all tab links inside the container are visible
    print("\n--- Verifying All Tab Links Inside Container ---")
    menu_items = page.locator(AmazonTabsLocator.MENU_ITEMS) 
    
    # Wait for at least one menu item to be visible to ensure the menu has loaded
    expect(menu_items.first).to_be_visible(timeout=5000)
    
    # Get the count of all menu items found
    menu_item_count = menu_items.count()
    print(f"✅ Found {menu_item_count} total menu items inside the hamburger menu.")

# Step 3: Load Expected List from JSON file
    # This dynamically finds your 'data' folder on Windows safely
    data_file = Path(__file__).parent.parent / "data" / "hamburger_menu.json"
    
    with open(data_file, "r") as file:
        expected_menu_items = json.load(file)

    # Step 4: Extract actual text from the webpage into a Python list
    actual_texts = []
    for i in range(menu_item_count):
        item_text = menu_items.nth(i).inner_text().strip()
        if item_text:  # Only add it if it's not an empty string
            actual_texts.append(item_text)

    # Step 5: Verify expected items exist in the actual list
    missing_items = []
    print("\n--- Cross-Checking Expected Items ---")
    for expected_item in expected_menu_items:
        if expected_item in actual_texts:
            print(f"  ✅ Verified present: {expected_item}")
        else:
            missing_items.append(expected_item)
            print(f"  ❌ MISSING: {expected_item}")

    # Step 6: The Final Assertion
    # If the missing_items list is not empty, the test fails and prints exactly what was missing.
    assert len(missing_items) == 0, f"Test Failed! Missing these menu items: {missing_items}"
    
    print("\n✅ All 60 expected menu items verified successfully!")