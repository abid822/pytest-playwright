import pytest

from pages.cell_phones_page import CellPhonesPage


@pytest.mark.desktop_only
@pytest.mark.cell_phones
def test_cell_phones_category_shows_a_price(cell_phones_page: CellPhonesPage):
    """Opens Cell Phones & Accessories, checks the store categories, and opens Cell Phones to see a price."""
    # Step 1: Open the Cell Phones & Accessories store
    cell_phones_page.open_cell_phones()
    # Step 2: Core store categories are listed
    cell_phones_page.expect_core_categories()
    # Step 3: Open Cell Phones
    cell_phones_page.open_category("Cell Phones")
    # Step 4: A product on that page shows a price
    cell_phones_page.expect_priced_product()
