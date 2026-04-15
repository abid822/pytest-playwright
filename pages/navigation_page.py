from playwright.sync_api import expect
from locators.amazon_locators import AmazonHomeLocators
from locators.amazon_login_pg_locators import AmazonLoginLocators

class AmazonNavigationPage:
    # This acts like a constructor in Java. It receives the browser page.
    def __init__(self, page):
        self.page = page
# Here is the method you will "call" from your tests
    def navigate_to_amazon_page(self):
        # STEP 1: Navigate
        print("\n---Navigating to Amazon ---")
        self.page.goto(AmazonHomeLocators.URL)
        expect(self.page).to_have_url(AmazonHomeLocators.URL)
        
        if self.page.url != AmazonHomeLocators.URL:
            print(f"❌ Expected URL {AmazonHomeLocators.URL} but got {self.page.url}")
            assert False, f"Expected URL {AmazonHomeLocators.URL} but got {self.page.url}"
        else:
            print("✅ Successfully navigated to Amazon.")