import pytest

from pages.find_a_gift_page import FindAGiftPage


@pytest.mark.find_a_gift
def test_find_a_gift_birthday_shows_a_price(find_a_gift_page: FindAGiftPage):
    """Opens Find a Gift and checks the shop sections."""
    # Step 1: Open the Gift Shop
    find_a_gift_page.open_find_a_gift()
    # Step 2: Occasion, interest, and recipient sections are listed
    find_a_gift_page.expect_shop_sections()
