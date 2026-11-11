import pytest

from pages.pet_supplies_page import PetSuppliesPage


@pytest.mark.desktop_only
@pytest.mark.pet_supplies
def test_pet_supplies_dogs_shows_a_price(pet_supplies_page: PetSuppliesPage):
    """Opens Pet Supplies, checks the store categories, and opens Dogs to see a price."""
    # Step 1: Open the Pet Supplies store
    pet_supplies_page.open_pet_supplies()
    # Step 2: Core store categories are listed
    pet_supplies_page.expect_core_categories()
    # Step 3: Open Dogs
    pet_supplies_page.open_category("Dogs")
    # Step 4: A product on that page shows a price
    pet_supplies_page.expect_priced_product()
