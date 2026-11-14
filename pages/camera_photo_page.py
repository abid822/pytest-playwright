import re

from playwright.sync_api import Page, expect

from locators.camera_photo_locators import CameraPhotoLocators
from pages.base_page import BasePage

# Departments that stay in the Camera & Photo strip. Seasonal tiles below them rotate.
CORE_CATEGORIES = [
    "DSLR Cameras",
    "Mirrorless Cameras",
    "Lenses",
    "Camcorders",
]


class CameraPhotoPage(BasePage):
    """Amazon Camera & Photo: store categories, then a priced camcorder."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.subnav = page.locator(CameraPhotoLocators.SUBNAV)

    def _camera_photo_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Camera & Photo$", re.I)
        )

    def _camera_photo_ready(self) -> bool:
        heading = self._camera_photo_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_camera_photo(self) -> None:
        # Step 1: Open the Camera & Photo store.
        # The first response is sometimes a shell with no heading.
        self.open(CameraPhotoLocators.URL)
        if not self._camera_photo_ready():
            self.page.goto(CameraPhotoLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Camera & Photo store is showing, not a bot checkpoint.
        # The document title says "Camera & Photo".
        expect(self.page).to_have_url(re.compile(r"node=502394"))
        expect(self.page).to_have_title(re.compile(r"Camera & Photo", re.I))
        expect(self._camera_photo_heading().first).to_be_visible()

    def _category_link(self, name: str):
        # Link text includes surrounding whitespace. The accessible name also
        # adds drop-down help, so match the visible label inside the strip.
        return self.page.locator(CameraPhotoLocators.SUBNAV_LINK).filter(
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
        assert not missing, f"Missing Camera & Photo categories: {missing}"
