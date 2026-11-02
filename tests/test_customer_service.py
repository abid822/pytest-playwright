import pytest

from pages.customer_service_page import CustomerServicePage


@pytest.mark.help
def test_customer_service_shipping_topic_lists_articles(
    customer_service_page: CustomerServicePage,
):
    # Step 1: Open Amazon Customer Service
    customer_service_page.open_customer_service()
    # Step 2: Help library search is ready
    customer_service_page.expect_help_search()
