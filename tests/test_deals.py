import pytest

from pages.deals_page import DealsPage


@pytest.mark.deals
def test_todays_deals_electronics_lists_priced_products(deals_page: DealsPage):
    """Opens Today's Deals, checks the core filters, and opens Electronics to see priced deal cards."""
    # Step 1: Open Today's Deals
    deals_page.open_deals()
    # Step 2: Deal cards show a price or a discount
    deals_page.expect_priced_deal_cards()
    # Step 3: Core filters are listed
    deals_page.expect_core_filters()
    # Step 4: Electronics filter keeps priced deals on the page
    deals_page.open_filter("Electronics", "electronics")
    deals_page.expect_priced_deal_cards()
