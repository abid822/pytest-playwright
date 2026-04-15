import pytest
import os
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import expect 
from locators.amazon_locators import AmazonHomeLocators
from locators.amazon_login_pg_locators import AmazonLoginLocators
from pages.amazon_login_actions import AmazonLoginActions


@pytest.mark.login
@pytest.mark.smoke
def test_amazon_login_page_pixelmatch(sb_page):
    # 1. Give the browser to your actions class

    actions = AmazonLoginActions(sb_page)
    # 2. CALL YOUR SETUP STEPS! (Explicitly, with parentheses)
    actions.navigate_to_login_screen()



    # STEP 4: The Pixelmatch Visual Comparison
    wait_time = 2000  # milliseconds
    print("--- Step 4: Taking screenshot and running Pixelmatch ---")
    # Define where the images will live
    actual_path = "reports/step_4_actual.png"
    baseline_path = "baselines/amazonInitialloginpage.png"
    diff_path = "reports/step_4_failed_diff.png"
    
    # 1. Ensure the folders exist (exist_ok=True means it won't crash if they are already there)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("baselines", exist_ok=True)
    
    # 2. Take the actual screenshot for this specific test run
    sb_page.screenshot(path=actual_path)
    
    # 3. Auto-Heal: If the baseline doesn't exist yet, create it right now!
    if not os.path.exists(baseline_path):
        print(f"⚠️ Baseline missing! Creating a new Gold Standard image at: {baseline_path}")
        sb_page.screenshot(path=baseline_path)
    
    # 4. Open both images using Pillow
    img_baseline = Image.open(baseline_path)
    img_actual = Image.open(actual_path)
    
    # 5. Safety Check: Images must be the exact same size to compare pixels
    assert img_baseline.size == img_actual.size, f"Size mismatch! Baseline is {img_baseline.size}, Actual is {img_actual.size}"
    
    # 6. Create a blank canvas to hold the "difference" picture
    img_diff = Image.new("RGBA", img_baseline.size)
    
    # 7. Run the Pixelmatch algorithm
    mismatched_pixels = pixelmatch(
        img_baseline, 
        img_actual, 
        img_diff, 
        threshold=0.1,  # 0.1 allows for tiny, invisible rendering differences
        includeAA=True  # Ignores text anti-aliasing differences
    )
    
    # 8. Evaluate the results
    if mismatched_pixels > 0:
        # Save the red-highlighted difference image so you can see what failed
        img_diff.save(diff_path)
        pytest.fail(f"❌ Visual mismatch! {mismatched_pixels} pixels were different. Check {diff_path} to see the errors.")
    else:
        print("✅ Pixelmatch passed! The screen is a visual match.")
