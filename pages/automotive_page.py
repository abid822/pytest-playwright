import re

from playwright.sync_api import Page, expect

from locators.amazon_automotive_locators import AmazonAutomotiveLocators
from pages.home_page import HomePage


class AutomotivePage(HomePage):
    """Amazon Automotive store and Your Garage add-vehicle flow."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.automotive_nav = page.get_by_role("link", name=re.compile(r"^Automotive$", re.I))
        self.your_garage = page.get_by_role("link", name=re.compile(r"Your Garage", re.I))
        self.add_first_vehicle = page.get_by_role(
            "button", name=re.compile(r"Add your first vehicle|Add a vehicle", re.I)
        )
        self.select_new_vehicle = page.locator(AmazonAutomotiveLocators.ADD_VEHICLE)
        self.vehicle_type = page.locator(AmazonAutomotiveLocators.VEHICLE_TYPE)
        self.year = page.locator(AmazonAutomotiveLocators.YEAR)
        self.make = page.locator(AmazonAutomotiveLocators.MAKE)
        self.model = page.locator(AmazonAutomotiveLocators.MODEL)
        self.save = page.locator(AmazonAutomotiveLocators.SAVE)
        self.success = page.locator(AmazonAutomotiveLocators.SUCCESS)
        self.more_info_needed = page.get_by_text(
            re.compile(AmazonAutomotiveLocators.MORE_INFO_NEEDED, re.I)
        )

    def open_automotive(self) -> None:
        # Step 1: Start on Amazon home
        self.open_home()
        # Step 2: Click Automotive in the top nav
        expect(self.automotive_nav.first).to_be_visible()
        self.automotive_nav.first.click()
        expect(self.page).to_have_url(re.compile(r"automotive", re.I))

    def open_your_garage(self) -> None:
        # Step 3: Open Your Garage
        expect(self.your_garage.first).to_be_visible()
        self.your_garage.first.click()
        expect(self.page).to_have_url(re.compile(r"your-garage", re.I))

    def open_add_vehicle_form(self) -> None:
        # Step 4: Open the add-vehicle modal
        expect(self.add_first_vehicle.first).to_be_visible()
        self.add_first_vehicle.first.click()
        expect(self.page.get_by_role("dialog")).to_be_visible()
        # Step 5: Switch from license plate to Year / Make / Model
        self.select_new_vehicle.scroll_into_view_if_needed()
        self.select_new_vehicle.evaluate("el => el.click()")
        expect(self.year).to_be_visible()

    def _pick_dropdown(self, dropdown, option_label: str) -> None:
        # Amazon uses a custom listbox; pick by accessible option name
        expect(dropdown).to_be_visible()
        dropdown.click()
        listbox = self.page.get_by_role("listbox")
        expect(listbox).to_be_visible()
        option = listbox.get_by_role("option", name=re.compile(rf"^{re.escape(option_label)}$", re.I))
        if option.count() == 0:
            option = listbox.get_by_role("option", name=re.compile(option_label, re.I))
        expect(option.first).to_be_visible()
        option.first.click()

    def add_vehicle(self, year: str, make: str, model: str) -> None:
        # Tesla lists Model 3 as "3" in the Model dropdown
        model_option = "3" if re.search(r"model\s*3", model, re.I) else model
        # Step 6: Choose vehicle type, then year, make, model
        self._pick_dropdown(self.vehicle_type, "Car, Truck, SUV or Van")
        self._pick_dropdown(self.year, year)
        self._pick_dropdown(self.make, make)
        self._pick_dropdown(self.model, model_option)
        # Step 7: Save to Your Garage
        expect(self.save).to_be_enabled()
        self.save.click()

    def report_more_vehicle_information_needed(self) -> bool:
        # Print whether Amazon shows the extra-info banner; do not fail either way
        try:
            self.more_info_needed.first.wait_for(state="visible", timeout=5000)
            shown = True
        except Exception:
            shown = False
        if shown:
            print('\n"More vehicle information needed" is SHOWN\n')
        else:
            print('\n"More vehicle information needed" is NOT shown\n')
        return shown

    def expect_vehicle_in_garage(self, year: str, make: str, model: str) -> None:
        # Confirm the added vehicle shows on the garage (or success banner)
        expect(self.page.get_by_text(make, exact=False).first).to_be_visible()
        expect(self.page.get_by_text(year, exact=False).first).to_be_visible()
        expect(self.page.get_by_text(re.compile(rf"{re.escape(model)}|\b3\b", re.I)).first).to_be_visible()
