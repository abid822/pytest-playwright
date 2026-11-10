import pytest

from pages.video_games_page import VideoGamesPage


@pytest.mark.desktop_only
@pytest.mark.video_games
def test_video_games_digital_shows_a_price(video_games_page: VideoGamesPage):
    """Opens Video Games, checks the store categories, and opens Digital Games to see a price."""
    # Step 1: Open the Video Games store
    video_games_page.open_video_games()
    # Step 2: Core store categories are listed
    video_games_page.expect_core_categories()
    # Step 3: Open Digital Games
    video_games_page.open_category("Digital Games")
    # Step 4: A product on that page shows a price
    video_games_page.expect_priced_product()
