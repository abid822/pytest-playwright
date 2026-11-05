import pytest

from pages.find_a_gift_page import FindAGiftPage


@pytest.mark.find_a_gift
def test_find_a_gift_birthday_shows_a_price(find_a_gift_page: FindAGiftPage):
    """Opens Find a Gift, checks the shop sections, and opens Birthdays to see a gift with a price."""
    # Step 1: Open the Gift Shop
    find_a_gift_page.open_find_a_gift()
    # Step 2: Occasion, interest, and recipient sections are listed
    find_a_gift_page.expect_shop_sections()
    # Step 3: Birthdays and other occasions are offered
    find_a_gift_page.expect_occasions()
    # Step 4: For Her, For Him, For Teens, and For Kids are offered
    find_a_gift_page.expect_recipients()
    # Step 5: Open Birthdays
    find_a_gift_page.open_birthdays()
    # Step 6: A birthday gift has a title and a price
    find_a_gift_page.expect_priced_gift()
