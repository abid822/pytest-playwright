import pytest

from pages.customer_service_page import CustomerServicePage


@pytest.mark.help
def test_customer_service_shipping_topic_lists_articles(
    customer_service_page: CustomerServicePage,
):
    """Opens Customer Service, checks the help search, and opens Shipping and Delivery articles."""
    # Step 1: Open Amazon Customer Service
    customer_service_page.open_customer_service()
    # Step 2: Help library search is ready
    customer_service_page.expect_help_search()
    # Step 3: Core help topics are listed
    customer_service_page.expect_core_topics()
    # Step 4: Shipping and Delivery lists articles
    customer_service_page.open_topic("Shipping and Delivery")
    customer_service_page.expect_topic_articles(
        [
            "Shipping Rates and Times",
            "Amazon Prime Shipping Benefits",
        ]
    )
