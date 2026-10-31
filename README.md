# pytest-playwright

Pytest + Playwright UI tests for Amazon.com.

Abidur Chowdhury built the original framework. Later work (pages, reports, garage/cart flows) was updated and tested with Cursor.

Amazon is a live site. Captchas, geo, and A/B tests can fail a run even when the code is fine.

## How the suite is organized

One feature = **three layers**. Specs never hold CSS; locators never click.

| Layer | Folder | Owns |
| --- | --- | --- |
| Spec | `tests/` | Ordered steps and assertions only |
| Page | `pages/` | Clicks, typing, waits |
| Locator | `locators/` | CSS / role selectors |

Also:

| Path | Role |
| --- | --- |
| `conftest.py` | Browser launch + page fixtures |
| `config/settings.py` | Base URL, Chrome, timeouts (from `.env`) |
| `data/` | JSON baselines (hamburger menu) |
| `baselines/` | Pixelmatch images |
| `utils/` | HTML dashboard + screenshot compare |

```
tests/test_login.py  →  pages/login_page.py  →  locators/login_locators.py
tests/test_nav_*.py  →  pages/home_page.py   →  locators/nav_locators.py
tests/test_cart.py   →  home + search pages  →  locators/home_locators.py
tests/test_automotive.py → pages/automotive_page.py → locators/automotive_locators.py
```

## Setup

Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Watch the browser: `HEADLESS=false`, `BROWSER_CHANNEL=chrome`, `SLOW_MO=250` in `.env`.

## Run

```bash
pytest -v
pytest tests/test_automotive.py -v
pytest -m smoke
pytest -m login
pytest -m tabs
pytest -m cart
pytest -m automotive
pytest -m search
pytest -m language
```

After a run open `reports/report.html` (plain-language cards). Engineer dump: `reports/pytest-debug.html`.

## Add a test

1. Put selectors in `locators/<area>_locators.py` (`HomeLocators`, `NavLocators`, …).
2. Put actions on the matching class in `pages/`.
3. Put the scenario in `tests/test_<area>.py` with `# Step N:` comments and a pytest marker.
4. Add a short story in `utils/friendly_report.py` `STORIES` so the HTML report reads in English.

Do not import locators from tests.

## Tests

| File | What it checks |
| --- | --- |
| `test_login.py` | Bad email is rejected |
| `test_login_visual.py` | Sign-in form vs baseline image |
| `test_nav_tabs.py` | Best Sellers, Deals, Prime, Sell |
| `test_nav_container.py` | Top nav strip exists |
| `test_nav_hamburger.py` | All menu + scrollbar |
| `test_cart.py` | Cheap cable in the cart |
| `test_search_pagination.py` | Page 2 is a different product set |
| `test_automotive.py` | Tesla garage, cheapest seat covers, cart screenshots |
| `test_language.py` | EN selected, Spanish offered, not saved |

## Markers

`smoke`, `login`, `cart`, `tabs`, `automotive`, `search`, `language` — see `pytest.ini`.
