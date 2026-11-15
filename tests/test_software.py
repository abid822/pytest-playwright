import pytest

from pages.software_page import SoftwarePage


@pytest.mark.desktop_only
@pytest.mark.software
def test_software_for_students_shows_a_price(software_page: SoftwarePage):
    """Opens Software, checks the store categories, and opens Software for Students to see a price."""
    # Step 1: Open the Software store
    software_page.open_software()
    # Step 2: Core store categories are listed
    software_page.expect_core_categories()
    # Step 3: Open Software for Students
    software_page.open_category("Software for Students")
    # Step 4: A product on that page shows a price
    software_page.expect_priced_product()
