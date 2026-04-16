import pytest
import os
import base64
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context_managed():
    # Setup the 'Human' profile folder
# Setup the 'Human' profile folder
    user_data_dir = os.path.join(os.getcwd(), "user_data")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            slow_mo=500,
            # We use '--start-fullscreen' instead of '--start-maximized'
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--start-fullscreen" 
            ],
            # This must be True so Playwright doesn't force a small viewport
            no_viewport=True 
        )
        yield context
        context.close()

@pytest.fixture
def sb_page(browser_context_managed, request):
    page = browser_context_managed.new_page()
    
    # ⚠️ CRITICAL STEP: We attach the page to the 'request' object.
    # This allows the screenshot hook below to find the active browser window.
    request.node.page = page 
    
    yield page
    page.close()


# =================================================================
# REPORTING HOOK: Takes screenshots on Failure or Skip
# =================================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # This executes the test and gets the result
    outcome = yield
    report = outcome.get_result()
    
    # 'extras' is where pytest-html stores extra data like images
    extras = getattr(report, "extras", [])

    # We only care about the moment the test actually executes ("call")
    if report.when == "call":
        # Check if the test failed or skipped
        if report.failed or report.skipped:
            # Grab the active page object we attached in the fixture earlier
            page = getattr(item, "page", None)
            
            if page:
                # 1. Take the screenshot in memory (bytes)
                screenshot_bytes = page.screenshot()
                
                # 2. Convert it to a Base64 string (embeds it directly into HTML)
                b64_img = base64.b64encode(screenshot_bytes).decode()
                
                # 3. Create the HTML image tag
                import pytest_html
                html_snippet = f'<div><img src="data:image/png;base64,{b64_img}" alt="screenshot" style="width:600px;height:auto;border:2px solid red;margin-top:10px;" /></div>'
                
                # 4. Attach it to the report
                extras.append(pytest_html.extras.html(html_snippet))
    
    # Save the attachments back to the report
    report.extras = extras