import pytest

from pages.registry_page import RegistryPage


@pytest.mark.registry
def test_baby_registry_offers_find_by_name(registry_page: RegistryPage):
    """Opens Amazon Registry and then Baby Registry."""
    # Step 1: Open Amazon Registry
    registry_page.open_registry()
    # Step 2: Open Baby Registry
    registry_page.open_baby_registry()
