import pytest

from pages.cart_page import CartPage


@pytest.mark.cart
def test_empty_cart_offers_sign_in_and_deals(cart_page: CartPage):
    """Opens an empty cart and checks the zero count, sign-in, and Today's Deals."""
    # Step 1: Open the shopping cart
    cart_page.open_cart()
    # Step 2: The cart says it is empty and the header count is 0
    cart_page.expect_empty()
    # Step 3: Sign in and Today's Deals are offered
    cart_page.expect_sign_in_and_deals()
