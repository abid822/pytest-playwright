import pytest

from pages.musical_instruments_page import MusicalInstrumentsPage


@pytest.mark.desktop_only
@pytest.mark.musical_instruments
def test_musical_instruments_amplifiers_shows_a_price(
    musical_instruments_page: MusicalInstrumentsPage,
):
    # Step 1: Open the Musical Instruments store
    musical_instruments_page.open_musical_instruments()
    # Step 2: Core store categories are listed
    musical_instruments_page.expect_core_categories()
