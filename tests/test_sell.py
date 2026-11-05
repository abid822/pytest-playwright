import pytest

from pages.sell_page import SellPage


@pytest.mark.sell
def test_sell_page_shows_priced_selling_plans(sell_page: SellPage):
    """Opens Sell on Amazon, checks the account steps, and opens selling plans to see Individual and Professional prices."""
    # Step 1: Open the Sell page
    sell_page.open_sell()
    # Step 2: Choose a plan, create an account, and start selling are listed
    sell_page.expect_start_steps()
    # Step 3: Open selling plans
    sell_page.open_selling_plans()
    # Step 4: Individual and Professional each show a price
    sell_page.expect_priced_plans()
