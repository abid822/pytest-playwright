import pytest

from pages.camera_photo_page import CameraPhotoPage


@pytest.mark.desktop_only
@pytest.mark.camera_photo
def test_camera_photo_camcorders_shows_a_price(camera_photo_page: CameraPhotoPage):
    # Step 1: Open the Camera & Photo store
    camera_photo_page.open_camera_photo()
    # Step 2: Core store categories are listed
    camera_photo_page.expect_core_categories()
    # Step 3: Open Camcorders
    camera_photo_page.open_category("Camcorders")
    # Step 4: A product on that page shows a price
    camera_photo_page.expect_priced_product()
