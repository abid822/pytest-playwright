# pytest-playwright

Pytest and Playwright tests for Amazon.com. Each check is a page object calling locators: specs hold the steps, `pages/` holds the clicks and waits, and `locators/` holds the selectors. Visual checks compare a screenshot to a saved image with pixelmatch. Every run also writes a plain-language HTML report.

Amazon is a live site. A captcha, a regional layout, or an experiment can fail a test when the code has not changed.

## Layout

| Path | Contents |
| --- | --- |
| `config/` | `settings.py` — base URL, browser, timeouts, and viewport from the environment |
| `locators/` | Selectors: `HomeLocators`, `SearchLocators`, `LanguageLocators`, `LoginLocators`, `NavLocators`, `AutomotiveLocators` |
| `pages/` | Page objects: `BasePage`, `HomePage`, `LoginPage`, `SearchResultsPage`, `AutomotivePage` |
| `tests/` | Pytest modules. Specs call page objects and leave selectors in `locators/` |
| `utils/` | `friendly_report.py` (HTML summary) and `visual.py` (pixelmatch) |
| `data/` | `hamburger_menu.json` — expected labels in the All menu |
| `baselines/` | `amazon_login_form.png` for the sign-in visual check |
| `assets/` | `style.css`, a pytest-html stylesheet kept in the repo. The debug report is self-contained and carries its own CSS |
| `conftest.py` | Browser launch, page fixtures, and the report hooks |
| `pytest.ini` | Test path, markers, and the pytest-html report |
| `requirements.txt` | pytest, Playwright, pytest-html, Pillow, pixelmatch |
| `.env.example` | Sample values for the variables below |

`utils/visual.py` uses `baselines/amazon_login_form.<platform>.png` when that file exists (for example `amazon_login_form.darwin.png`). Otherwise it uses `baselines/amazon_login_form.png`.

## Tests

| File | What it covers |
| --- | --- |
| `tests/test_login.py` | Opens sign-in from the header, submits `invalidemailgmail.com`, and expects the invalid-email error plus the helper links. Markers: `login`, `smoke`. |
| `tests/test_login_visual.py` | Opens sign-in and compares the login form to `baselines/amazon_login_form.png`. Marker: `login`. |
| `tests/test_nav_tabs.py` | Opens home and checks that Best Sellers, Today's Deals, Prime, and Sell are in the top nav. Markers: `smoke`, `tabs`. |
| `tests/test_nav_container.py` | Opens home, checks the top nav strip is visible, and checks that more than five tab links are present. Marker: `tabs`. |
| `tests/test_nav_hamburger.py` | Opens the All menu, requires every label in `data/hamburger_menu.json` (extra live items are printed only), drags the scrollbar, and checks that Sign in is visible. Markers: `tabs`, `smoke`. |
| `tests/test_cart.py` | Searches for `usb c charging cable`, adds the first result, and checks the header cart count is no longer 0. Markers: `cart`, `smoke`. |
| `tests/test_search_pagination.py` | Searches for `hardcover notebook`, records organic titles on page 1, opens page 2, and checks the titles changed. Marker: `search`. |
| `tests/test_automotive.py` | Opens Automotive, adds a 2023 Tesla Model 3 to Your Garage, logs whether "More vehicle information needed" is showing, searches seat covers, sorts Price: Low to High, adds the first result, opens the cart, and saves screenshots of both. Markers: `automotive`, `smoke`. |
| `tests/test_language.py` | Opens language settings from the header EN control. English stays selected, Spanish is offered, and the form is left unsaved. Marker: `language`. |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
set -a && source .env && set +a
```

On Windows, activate with `.venv\Scripts\activate`.

`config/settings.py` reads the process environment. Export `.env` as above, or pass the variables on the command line (`HEADLESS=true pytest`).

| Variable | Default | Role |
| --- | --- | --- |
| `BASE_URL` | `https://www.amazon.com/` | Site the tests open |
| `BROWSER_CHANNEL` | `chrome` | Playwright browser channel. `chrome` uses installed Google Chrome. An empty value uses the Chromium from `playwright install chromium` |
| `HEADLESS` | `false` | `1`, `true`, `yes`, or `on` hide the window. Any other value shows it |
| `SLOW_MO` | `250` when headed, `0` when headless | Milliseconds to pause between Playwright actions |
| `DEFAULT_TIMEOUT_MS` | `15000` | Timeout for actions and `expect` assertions |
| `VIEWPORT_WIDTH` | `1280` | Browser width in pixels |
| `VIEWPORT_HEIGHT` | `720` | Browser height in pixels |

## Run

From the repository root, with the virtualenv active and the variables exported:

```bash
pytest
pytest tests/test_cart.py
pytest tests/test_cart.py::test_add_cheap_cable_to_cart
pytest -m smoke
```

Headed is the default (`HEADLESS=false`): a visible Chrome window, with `SLOW_MO` at 250 ms unless you set it. Headless:

```bash
HEADLESS=true pytest
```

`pytest.ini` also defines `login`, `cart`, `tabs`, `automotive`, `search`, and `language`. `--strict-markers` is on, so an unknown marker fails collection.

## Reports

`reports/` is gitignored. A run writes:

- `reports/report.html` — plain-language cards (title, steps, outcome, and the error). A failed test includes a page screenshot when the browser can still capture one.
- `reports/pytest-debug.html` — pytest-html output configured in `pytest.ini`.

The automotive test also saves `reports/seat_covers_added_to_cart.png` and `reports/seat_covers_cart.png`.

On a visual mismatch, `utils/visual.py` writes `reports/amazon_login_form_actual.png` and `reports/amazon_login_form_diff.png`. If the baseline file is missing, that run saves the current screenshot as the baseline.
