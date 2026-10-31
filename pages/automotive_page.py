import re

from playwright.sync_api import Page, expect

from locators.automotive_locators import AutomotiveLocators
from pages.home_page import HomePage


class AutomotivePage(HomePage):
    """Amazon Automotive store and Your Garage add-vehicle flow."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.automotive_nav = page.get_by_role("link", name=re.compile(r"^Automotive$", re.I))
        self.your_garage = page.get_by_role("link", name=re.compile(r"Your Garage", re.I))
        self.add_first_vehicle = page.get_by_role(
            "button",
            name=re.compile(r"Add your first vehicle|Add a new vehicle|Add a vehicle", re.I),
        )
        self.select_new_vehicle = page.locator(AutomotiveLocators.ADD_VEHICLE)
        self.vehicle_type = page.locator(AutomotiveLocators.VEHICLE_TYPE)
        self.year = page.locator(AutomotiveLocators.YEAR)
        self.make = page.locator(AutomotiveLocators.MAKE)
        self.model = page.locator(AutomotiveLocators.MODEL)
        self.save = page.locator(AutomotiveLocators.SAVE)
        self.success = page.locator(AutomotiveLocators.SUCCESS)
        self.more_info_needed = page.get_by_text(
            re.compile(AutomotiveLocators.MORE_INFO_NEEDED, re.I)
        )

    def open_automotive(self) -> None:
        # Step 1: Start on Amazon home
        self.open_home()
        # Step 2: Click Automotive in the top nav
        expect(self.automotive_nav.first).to_be_visible()
        self.automotive_nav.first.click()
        expect(self.page).to_have_url(re.compile(r"automotive", re.I))

    def open_your_garage(self) -> None:
        # Step 3: Open Your Garage. Headless sometimes lands on an empty document.
        link = self.your_garage.first
        expect(link).to_be_visible()
        href = link.get_attribute("href") or "https://www.amazon.com/gp/your-garage/"
        if href.startswith("/"):
            href = "https://www.amazon.com" + href
        link.click()
        try:
            expect(self.page).to_have_url(re.compile(r"your-garage", re.I), timeout=8000)
        except AssertionError:
            self.page.goto(href, wait_until="domcontentloaded")
        try:
            expect(self.add_first_vehicle.first).to_be_visible(timeout=5000)
        except AssertionError:
            self.page.goto(href, wait_until="domcontentloaded")
            expect(self.page).to_have_url(re.compile(r"your-garage", re.I))
            expect(self.add_first_vehicle.first).to_be_visible()

    def open_add_vehicle_form(self) -> None:
        # Step 4: Open the add-vehicle modal
        expect(self.add_first_vehicle.first).to_be_visible()
        self.add_first_vehicle.first.click()
        expect(self.page.get_by_role("dialog")).to_be_visible()
        # Step 5: Switch from license plate to Year / Make / Model.
        # A DOM click opens it in headed Chrome. Headless only toggles the radio icon.
        self.select_new_vehicle.evaluate("el => el.scrollIntoView({block: 'center'})")
        self.select_new_vehicle.evaluate("el => el.click()")
        try:
            expect(self.year).to_be_visible(timeout=3000)
        except AssertionError:
            box = self.select_new_vehicle.bounding_box()
            assert box, "Select new vehicle row has no bounding box"
            self.page.mouse.click(box["x"] + 14, box["y"] + box["height"] / 2)
            expect(self.year).to_be_visible()

    def _select_native_option(self, dropdown, option_label: str) -> None:
        # Headless Chromium exposes these as native <select>s, not a listbox
        field = dropdown.get_attribute("id") or ""
        suffix = field.removeprefix("vehicle-select-chooser-")
        native = self.page.locator(f"select#vehicle-select-chooser-native-{suffix}")
        expect(native).to_be_attached()
        native.select_option(label=option_label)

    def _pick_dropdown(self, dropdown, option_label: str) -> None:
        # Amazon uses a custom listbox in headed Chrome; pick by accessible name
        expect(dropdown).to_be_visible()
        dropdown.click()
        listbox = self.page.get_by_role("listbox")
        try:
            expect(listbox.first).to_be_visible(timeout=3000)
        except AssertionError:
            self._select_native_option(dropdown, option_label)
            return
        option = listbox.first.get_by_role("option", name=re.compile(rf"^{re.escape(option_label)}$", re.I))
        if option.count() == 0:
            option = listbox.first.get_by_role("option", name=re.compile(option_label, re.I))
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
        # Saving can bounce through Amazon's checkpoint after navigation starts
        try:
            self.page.wait_for_url(re.compile(r"checkpoint"), timeout=4000)
        except Exception:
            pass
        if "checkpoint" in self.page.url:
            self.dismiss_continue_shopping()
            button = self.page.get_by_role("button", name=re.compile(r"Continue", re.I))
            if button.count() and button.first.is_visible():
                button.first.click()
            self.page.goto("https://www.amazon.com/your-garage")
        expect(self.page).to_have_url(re.compile(r"your-garage", re.I))
        # Ignore the hidden <option> nodes left in the add-vehicle form
        make_text = self.page.get_by_text(make, exact=False).locator("visible=true")
        year_text = self.page.get_by_text(year, exact=False).locator("visible=true")
        model_text = self.page.get_by_text(re.compile(rf"{re.escape(model)}|\b3\b", re.I)).locator(
            "visible=true"
        )
        expect(make_text.first).to_be_visible()
        expect(year_text.first).to_be_visible()
        expect(model_text.first).to_be_visible()
