import re

from playwright.sync_api import Page, expect

from locators.pet_supplies_locators import PetSuppliesLocators
from pages.base_page import BasePage

# Animals that stay in the Pet Supplies strip. Seasonal tiles below them rotate.
CORE_CATEGORIES = [
    "Dogs",
    "Cats",
    "Fish & Aquatics",
    "Small Animals",
]


class PetSuppliesPage(BasePage):
    """Amazon Pet Supplies: store categories, then a priced Dogs product."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(PetSuppliesLocators.SUBNAV)

    def _pet_supplies_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Pet Supplies$", re.I)
        )

    def _pet_supplies_ready(self) -> bool:
        heading = self._pet_supplies_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_pet_supplies(self) -> None:
        # Step 1: Open the Pet Supplies store.
        # The first response is sometimes a shell with no heading.
        self.open(PetSuppliesLocators.URL)
        if not self._pet_supplies_ready():
            self.page.goto(PetSuppliesLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Pet Supplies store is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"node=2619533011"))
        expect(self.page).to_have_title(re.compile(r"Pet Supplies", re.I))
        expect(self._pet_supplies_heading().first).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(PetSuppliesLocators.SUBNAV_LINK).filter(
            has_text=re.compile(re.escape(name), re.I)
        ).first

    def expect_core_categories(self, names: list[str] | None = None) -> None:
        # Step 1: The store strip is on screen
        expect(self.subnav).to_be_visible()
        # Step 2: Each core category is listed
        missing = []
        for name in names or CORE_CATEGORIES:
            link = self._category_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Pet Supplies categories: {missing}"
