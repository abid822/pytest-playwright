import pytest

from pages.amazon_devices_page import AmazonDevicesPage


@pytest.mark.desktop_only
@pytest.mark.amazon_devices
def test_amazon_devices_kindle_shows_a_price(amazon_devices_page: AmazonDevicesPage):
    """Opens Amazon Devices, checks the store sections, and opens Kindle to see a price."""
    # Step 1: Open the Amazon Devices store
    amazon_devices_page.open_amazon_devices()
    # Step 2: Core store sections are listed
    amazon_devices_page.expect_core_categories()
    # Step 3: Open Kindle
    amazon_devices_page.open_kindle()
    # Step 4: A Kindle e-reader shows a price
    amazon_devices_page.expect_priced_product()
