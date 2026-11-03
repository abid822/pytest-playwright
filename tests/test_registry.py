import pytest

from pages.registry_page import RegistryPage


@pytest.mark.registry
def test_baby_registry_offers_find_by_name(registry_page: RegistryPage):
    """Opens Registry, checks Baby, Wedding, and Gift List, then opens Baby Registry to find a registry by name."""
    # Step 1: Open Amazon Registry
    registry_page.open_registry()
    # Step 2: Baby, Wedding, and Gift List are offered
    registry_page.expect_core_registries()
    # Step 3: Open Baby Registry
    registry_page.open_baby_registry()
    # Step 4: Find a baby registry by name is ready
    registry_page.expect_find_by_name()
