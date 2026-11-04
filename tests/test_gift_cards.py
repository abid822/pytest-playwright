import pytest

from pages.gift_cards_page import GiftCardsPage


@pytest.mark.gift_cards
def test_gift_cards_birthday_egift_shows_a_price(gift_cards_page: GiftCardsPage):
    # Step 1: Open the Gift Cards shop
    gift_cards_page.open_gift_cards()
    # Step 2: Occasion, brand, category, and delivery type are listed
    gift_cards_page.expect_shop_sections()
    # Step 3: Redeem and balance are offered
    gift_cards_page.expect_redeem_and_balance()
