[![Tests](https://github.com/abid822/pytest-playwright/actions/workflows/run-tests.yml/badge.svg)](https://github.com/abid822/pytest-playwright/actions/workflows/run-tests.yml)

# pytest-playwright

Pytest and Playwright tests for Amazon.com. Each check is a page object calling locators: specs hold the steps, `pages/` holds the clicks and waits, and `locators/` holds the selectors. Visual checks compare a screenshot to a saved image with pixelmatch. Every run also writes a plain-language HTML report.

Amazon is a live site. A captcha, a regional layout, or an experiment can fail a test when the code has not changed.

## Features

- Specs in `tests/` call page objects. Clicks and waits stay in `pages/`. Selectors stay in `locators/`.
- The sign-in visual check compares a screenshot to a Chromium baseline with pixelmatch.
- Every run writes a plain-language HTML report and a pytest-html debug report.
- `pytest -n auto` runs tests in parallel. Each worker launches its own browser, and the reports are merged at the end.
- `BROWSER` selects Chromium, Firefox, or WebKit. Chromium is the default.
- GitHub Actions runs that same suite on all three browsers.

## Layout

| Path | Contents |
| --- | --- |
| `config/` | `settings.py` — base URL, browser, timeouts, and viewport from the environment |
| `locators/` | Selectors: `HomeLocators`, `SearchLocators`, `LanguageLocators`, `LoginLocators`, `NavLocators`, `AutomotiveLocators` |
| `pages/` | Page objects: `BasePage`, `HomePage`, `LoginPage`, `SearchResultsPage`, `AutomotivePage` |
| `tests/` | Pytest modules. Specs call page objects and leave selectors in `locators/` |
| `utils/` | `friendly_report.py` (HTML summary) and `visual.py` (pixelmatch) |
| `data/` | `hamburger_menu.json` — All menu labels. The test asserts a stable core set and warns on the rest |
| `baselines/` | `amazon_login_form.png` for the sign-in visual check |
| `assets/` | `style.css`, a pytest-html stylesheet kept in the repo. The debug report is self-contained and carries its own CSS |
| `conftest.py` | Browser launch, page fixtures, and the report hooks |
| `pytest.ini` | Test path, markers, and the pytest-html report |
| `requirements.txt` | pytest, Playwright, pytest-html, pytest-rerunfailures, pytest-xdist, Pillow, pixelmatch |
| `.env.example` | Sample values for the variables below |

`utils/visual.py` uses `baselines/amazon_login_form.<platform>.png` when that file exists (for example `amazon_login_form.darwin.png`). Otherwise it uses `baselines/amazon_login_form.png`.

## Tests

| File | What it covers |
| --- | --- |
| `tests/test_login.py` | Opens sign-in from the header, submits `invalidemailgmail.com`, and expects the invalid-email error plus the helper links. Markers: `login`, `smoke`. |
| `tests/test_login_visual.py` | Opens sign-in and compares the login form to `baselines/amazon_login_form.png`. Markers: `login`, `chromium_only`. Skipped on Firefox and WebKit because the baseline is a Chromium screenshot. |
| `tests/test_nav_tabs.py` | Opens home and checks that Best Sellers, Today's Deals, Prime, and Sell are in the top nav. Markers: `smoke`, `tabs`. |
| `tests/test_nav_container.py` | Opens home, checks the top nav strip is visible, and checks that more than five tab links are present. Marker: `tabs`. |
| `tests/test_nav_hamburger.py` | Opens the All menu, requires a stable core set of labels (other JSON labels and extra live items are printed only), drags the scrollbar, and checks that Sign in is visible. Markers: `tabs`, `smoke`. |
| `tests/test_cart.py` | Searches for `usb c charging cable`, adds the first result, and checks the header cart count is no longer 0. Markers: `cart`, `smoke`. |
| `tests/test_search_pagination.py` | Searches for `hardcover notebook`, records organic titles on page 1, opens page 2, and checks the titles changed. Marker: `search`. |
| `tests/test_automotive.py` | Opens Automotive, adds a 2023 Tesla Model 3 to Your Garage, logs whether "More vehicle information needed" is showing, searches seat covers, sorts Price: Low to High, adds the first result, opens the cart, and saves screenshots of both. Markers: `automotive`, `smoke`, `ci_skip`. |
| `tests/test_language.py` | Opens language settings from the header EN control. English stays selected, Spanish is offered, and the form is left unsaved. Marker: `language`. |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install firefox
playwright install webkit
cp .env.example .env
set -a && source .env && set +a
```

On Windows, activate with `.venv\Scripts\activate`.

`config/settings.py` reads the process environment. Export `.env` as above, or pass the variables on the command line (`HEADLESS=true pytest`). `.env` is gitignored. `.env.example` is the sample that stays in the repo.

| Variable | Default | Role |
| --- | --- | --- |
| `BASE_URL` | `https://www.amazon.com/` | Site the tests open |
| `BROWSER` | `chromium` | `chromium`, `firefox`, or `webkit` |
| `BROWSER_CHANNEL` | `chrome` | Chromium only. `chrome` uses installed Google Chrome. An empty value uses Playwright's Chromium. Ignored for Firefox and WebKit |
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
pytest -n auto
HEADLESS=true BROWSER=firefox pytest -n auto
HEADLESS=true BROWSER=webkit pytest
```

Headed is the default (`HEADLESS=false`): a visible window, with `SLOW_MO` at 250 ms unless you set it. With `BROWSER=chromium` and `BROWSER_CHANNEL=chrome`, that window is Google Chrome. Headless:

```bash
HEADLESS=true pytest
```

`-n auto` (pytest-xdist) starts one worker per CPU. Each worker opens its own browser. `reports/report.html` and `reports/pytest-debug.html` are written once, after the workers finish. Screenshot files include the worker id so they do not overwrite each other, for example `reports/amazon_login_form_actual.gw0.png` and `reports/seat_covers_cart.gw0.png`. A normal run without `-n` keeps the unsuffixed names.

`pytest.ini` also defines `login`, `cart`, `tabs`, `automotive`, `search`, `language`, `ci_skip`, and `chromium_only`. `--strict-markers` is on, so an unknown marker fails collection.

## Continuous Integration

[`.github/workflows/run-tests.yml`](.github/workflows/run-tests.yml) runs on every push to `main`, on pull requests, every day at 13:00 UTC (`0 13 * * *`), and when the workflow is started by hand. The workflow uses `ubuntu-latest` and Python 3.12, caches pip, and installs `requirements.txt`.

The test job is a matrix over `chromium`, `firefox`, and `webkit` with `fail-fast: false`, so one browser does not cancel the others. Each job installs only that browser, with its system libraries (`playwright install --with-deps`). It sets `HEADLESS=true`, `SLOW_MO=0`, `BROWSER` to the matrix value, and an empty `BROWSER_CHANNEL` so Chromium is the Playwright build rather than installed Google Chrome. The other variables in `.env.example` (`BASE_URL`, `DEFAULT_TIMEOUT_MS`, `VIEWPORT_WIDTH`, `VIEWPORT_HEIGHT`) are set to those sample values. It runs `pytest -n auto -m "not ci_skip" --reruns 1`. The extra retry covers a dropped connection. It does not change what a test asserts.

`ci_skip` is for a test that cannot pass on a GitHub-hosted runner. Right now that is only `tests/test_automotive.py::test_add_2023_tesla_model_3_to_garage`: the Your Garage year/make/model control does not open in headless Chromium. It is deselected on every browser.

`chromium_only` is for the sign-in pixel check. The baseline image is Chromium. Firefox and WebKit skip that test instead of comparing against a screenshot they cannot match.

Each job uploads `reports/` as `reports-chromium`, `reports-firefox`, or `reports-webkit`, including when tests fail. Open the workflow run on GitHub and download the artifact for that browser. It contains `report.html` and `pytest-debug.html`.

## Reports

`reports/` is gitignored. A run writes:

- `reports/report.html` — plain-language cards (title, steps, outcome, and the error). A failed test includes a page screenshot when the browser can still capture one.
- `reports/pytest-debug.html` — pytest-html output configured in `pytest.ini`.

The automotive test also saves `reports/seat_covers_added_to_cart.png` and `reports/seat_covers_cart.png`.

On a visual mismatch, `utils/visual.py` writes `reports/amazon_login_form_actual.png` and `reports/amazon_login_form_diff.png`. If the baseline file is missing, that run saves the current screenshot as the baseline. Under `pytest -n`, those files include the worker id.

Author: Abidur Chowdhury, [abidur.net](https://abidur.net)
