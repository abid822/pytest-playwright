import pytest

from pages.prime_video_page import PrimeVideoPage


@pytest.mark.desktop_only
@pytest.mark.prime_video
def test_prime_video_storefront_shows_a_title(prime_video_page: PrimeVideoPage):
    """Opens Prime Video, checks a carousel is listed, and checks that a title card is showing."""
    # Step 1: Open the Prime Video storefront
    prime_video_page.open_prime_video()
    # Step 2: A carousel row has a heading
    prime_video_page.expect_carousel()
    # Step 3: A movie or show card shows a name
    prime_video_page.expect_title_card()
