class PharmacyLocators:
    URL = "https://pharmacy.amazon.com/"
    # Header and body links. The terms page is a different destination.
    # A hidden menu repeats "RxPass" without the leading slash.
    HOW_IT_WORKS_LINK = "a[href*='/how-it-works']"
    PILLPACK_LINK = "a[href*='/pillpack']"
    RXPASS_LINK = "a[href*='/rxpass']:not([href*='terms'])"
    # Medication finder. A label sits over the input.
    MED_SEARCH = "input.ap-search-bar__input"
    MED_SEARCH_LABEL = "span.ap-search-bar__input-label"
