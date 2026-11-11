[![Tests](https://github.com/abid822/pytest-playwright/actions/workflows/run-tests.yml/badge.svg)](https://github.com/abid822/pytest-playwright/actions/workflows/run-tests.yml)

# pytest-playwright

Pytest and Playwright tests for Amazon.com. Each check is a page object that calls locators: specs hold the steps, `pages/` holds the clicks and waits, and `locators/` holds the selectors. Visual checks compare a screenshot to a saved image with pixelmatch. Every run also writes a plain-language HTML report.

Amazon is a live site. When the continue-shopping check shows an "I am human" checkbox and a Continue button, the suite checks the box and clicks Continue. If that page is still up afterward, or an AI-agent interstitial appears, the test is skipped. A regional layout or an experiment can still fail a test when the code has not changed.

## Features

- Specs in `tests/` call page objects. Clicks and waits stay in `pages/`. Selectors stay in `locators/`.
- The sign-in visual check compares a screenshot to a Chromium baseline with pixelmatch.
- Every run writes a plain-language HTML report and a pytest-html debug report.
- `pytest -n auto` runs tests in parallel. Each worker launches its own browser, and the reports are merged at the end.
- `BROWSER` selects Chromium, Firefox, or WebKit. Chromium is the default.
- A failed test saves a Playwright trace under `test-results/traces/`. Open the zip at https://trace.playwright.dev. A passing test discards the trace.
- `--device desktop` (the default) keeps the 1280×720 viewport. `--device mobile` emulates an iPhone 14. Tests marked `desktop_only` are skipped on mobile.
- GitHub Actions runs that same suite on all three browsers.

## Layout

| Path | Contents |
| --- | --- |
| `config/` | `settings.py` — base URL, browser, timeouts, viewport, and the desktop or mobile device profile |
| `locators/` | Selectors: `HomeLocators`, `SearchLocators`, `LanguageLocators`, `LoginLocators`, `NavLocators`, `AutomotiveLocators`, `BestSellersLocators`, `CustomerServiceLocators`, `DealsLocators`, `RegistryLocators`, `NewReleasesLocators`, `GiftCardsLocators`, `SellLocators`, `FindAGiftLocators`, `AmazonHomeLocators`, `BooksLocators`, `BeautyLocators`, `ElectronicsLocators`, `BabyLocators`, `FooterLocators`, `SportsLocators`, `VideoGamesLocators` |
| `pages/` | Page objects: `BasePage`, `HomePage`, `LoginPage`, `SearchResultsPage`, `AutomotivePage`, `BestSellersPage`, `CustomerServicePage`, `DealsPage`, `RegistryPage`, `NewReleasesPage`, `GiftCardsPage`, `SellPage`, `FindAGiftPage`, `AmazonHomePage`, `BooksPage`, `BeautyPage`, `ElectronicsPage`, `BabyPage`, `FooterPage`, `SportsPage`, `VideoGamesPage` |
| `tests/` | Pytest modules. Specs call page objects and leave selectors in `locators/` |
| `utils/` | `friendly_report.py` (HTML summary) and `visual.py` (pixelmatch) |
| `data/` | `hamburger_menu.json` — All menu labels. The test asserts a stable core set and warns on the rest |
| `baselines/` | `amazon_login_form.png` for the sign-in visual check |
| `assets/` | `style.css`, a pytest-html stylesheet kept in the repo. The debug report is self-contained and carries its own CSS |
| `conftest.py` | Browser launch, device context, failure traces, page fixtures, and the report hooks |
| `pytest.ini` | Test path, markers (including `desktop_only`), and the pytest-html report |
| `requirements.txt` | pytest, Playwright, pytest-html, pytest-rerunfailures, pytest-xdist, Pillow, pixelmatch |
| `.env.example` | Sample values for the variables below |

`utils/visual.py` uses `baselines/amazon_login_form.<platform>.png` when that file exists (for example `amazon_login_form.darwin.png`). Otherwise it uses `baselines/amazon_login_form.png`.

## Tests

| File | What it covers |
| --- | --- |
| `tests/test_login.py` | Opens sign-in from the header, submits `invalidemailgmail.com`, and expects the invalid-email error plus the helper links. Also rejects each of the 4 fake pairs in `data/login_credentials.json`. An Amazon puzzle challenge skips that case. Markers: `login`, `smoke` (the single bad-email check only). |
| `tests/test_login_visual.py` | Opens sign-in and compares the login form to `baselines/amazon_login_form.png`. The email box is masked because its focus ring changes between runs. Markers: `login_visual`, `chromium_only`, `desktop_only`. Skipped on Firefox and WebKit because the baseline is a Chromium screenshot, and skipped with `--device mobile` because the baseline is the desktop form. |
| `tests/test_nav_tabs.py` | Opens home and checks that Best Sellers, Today's Deals, Prime, and Sell are in the top nav. Markers: `smoke`, `tabs`, `desktop_only`. |
| `tests/test_nav_container.py` | Opens home, checks the top nav strip is visible, and checks that more than five tab links are present. Markers: `tabs`, `desktop_only`. |
| `tests/test_nav_hamburger.py` | Opens the All menu, requires a stable core set of labels (other JSON labels and extra live items are only printed), drags the scrollbar, and checks that Sign in is visible. Markers: `tabs`, `smoke`, `desktop_only`. |
| `tests/test_cart.py` | Searches for `usb c charging cable`, adds the first result, and checks the header cart count is no longer 0. Markers: `cart`, `smoke`. |
| `tests/test_search_pagination.py` | Searches for `hardcover notebook`, records organic titles on page 1, opens page 2, and checks the titles changed. Markers: `search`, `desktop_only`. Mobile web has no numbered page strip. |
| `tests/test_search_no_results.py` | Searches for a query that matches nothing. Checks the empty-state message when Amazon shows it, and that no unsponsored product cards are listed. Marker: `search`. |
| `tests/test_search_four_stars.py` | Searches for `stainless steel water bottle`, applies 4 Stars & Up, and checks the filter stays selected with ratings of 4 or higher. Markers: `search`, `desktop_only`. The left-nav refinement is desktop-only. |
| `tests/test_automotive.py` | Opens Automotive, adds a 2023 Tesla Model 3 to Your Garage, logs whether "More vehicle information needed" is showing, searches seat covers, sorts Price: Low to High, adds the first result, opens the cart, and saves screenshots of both. Markers: `automotive`, `smoke`, `ci_skip`. |
| `tests/test_language.py` | Opens language settings from the header EN control. English stays selected, Spanish is offered, and the form is left unsaved. Marker: `language`. |
| `tests/test_bestsellers.py` | Opens Best Sellers, checks Books, Electronics, Home & Kitchen, and Toys & Games, then opens Electronics and checks the #1 product. Markers: `bestsellers`, `desktop_only`. The department column is desktop-only. |
| `tests/test_customer_service.py` | Opens Customer Service, checks the help search and the core topics, then opens Shipping and Delivery and checks that articles such as Shipping Rates and Times are listed. Marker: `help`. |
| `tests/test_deals.py` | Opens Today's Deals, checks Lightning deals, Electronics, Home, and Books, then opens Electronics and checks that deal cards still show a price or a discount. Marker: `deals`. |
| `tests/test_registry.py` | Opens Registry, checks Baby Registry, Wedding Registry, and Gift List, then opens Baby Registry and checks that find-by-name is ready. Marker: `registry`. |
| `tests/test_new_releases.py` | Opens New Releases, checks Books, Electronics, Home & Kitchen, and Computers & Accessories, then opens Electronics and checks the #1 product. Markers: `new_releases`, `desktop_only`. The department column is desktop-only. |
| `tests/test_gift_cards.py` | Opens Gift Cards, checks occasion, brand, category, and delivery type, then opens a Birthday eGift card and checks that it shows a price. Marker: `gift_cards`. |
| `tests/test_sell.py` | Opens Sell on Amazon, checks the account steps, then opens selling plans and checks that Individual and Professional each show a price. Marker: `sell`. |
| `tests/test_find_a_gift.py` | Opens Find a Gift, checks occasion, interest, and recipient, then opens Birthdays and checks that a gift shows a price. Marker: `find_a_gift`. |
| `tests/test_amazon_home.py` | Opens Amazon Home, checks Shop by Room, Furniture, Kitchen & Dining, and Bed & Bath, then opens Kitchen & Dining and checks that a product shows a price. Markers: `amazon_home`, `desktop_only`. The store category strip is desktop-only. |
| `tests/test_books.py` | Opens Books, checks the store sections and top categories, then opens Literature & Fiction and checks that a book shows a price. Marker: `books`. |
| `tests/test_beauty.py` | Opens Beauty, checks Makeup, Skin Care, Hair Care, and Fragrance, then opens Makeup and checks that a product shows a price. Markers: `beauty`, `desktop_only`. The store category strip is desktop-only. |
| `tests/test_electronics.py` | Opens Electronics, checks Cell Phones, Computers, TV & Video, and Headphones, then opens Headphones and checks that a product shows a price. Markers: `electronics`, `desktop_only`. The store category strip is desktop-only. |
| `tests/test_baby.py` | Opens the Baby store, checks Strollers, Car Seats, Nursery, and Feeding, then opens Strollers and checks that a product shows a price. Markers: `baby`, `desktop_only`. The store category strip is desktop-only. |
| `tests/test_footer.py` | Opens the home footer, checks Get to Know Us, Make Money with Us, Amazon Payment Products, and Let Us Help You, then uses Back to top. Markers: `footer`, `desktop_only`. The four-column footer is desktop-only. |
| `tests/test_sports.py` | Opens Sports & Outdoors, checks Outdoor Recreation, Cycling, Exercise & Fitness, and Golf, then opens Cycling and checks that a product shows a price. Markers: `sports`, `desktop_only`. The store category strip is desktop-only. |
| `tests/test_video_games.py` | Opens Video Games, checks PS5, Xbox Series X\|S, Switch, and PC, then opens Digital Games and checks that a product shows a price. Markers: `video_games`, `desktop_only`. The store category strip is desktop-only. |

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
pytest --device mobile
HEADLESS=true BROWSER=firefox pytest -n auto
HEADLESS=true BROWSER=webkit pytest
```

Headed is the default (`HEADLESS=false`): a visible window, with `SLOW_MO` at 250 ms unless you set it. With `BROWSER=chromium` and `BROWSER_CHANNEL=chrome`, that window is Google Chrome. Headless:

```bash
HEADLESS=true pytest
```

`-n auto` (pytest-xdist) starts one worker per CPU. Each worker opens its own browser. `reports/report.html` and `reports/pytest-debug.html` are written once, after the workers finish. Screenshot files include the worker id so they do not overwrite each other, for example `reports/amazon_login_form_actual.gw0.png` and `reports/seat_covers_cart.gw0.png`. A normal run without `-n` keeps the unsuffixed names.

`pytest.ini` also defines `login`, `cart`, `tabs`, `automotive`, `search`, `language`, `bestsellers`, `help`, `deals`, `registry`, `new_releases`, `gift_cards`, `sell`, `find_a_gift`, `amazon_home`, `books`, `beauty`, `electronics`, `baby`, `footer`, `sports`, `video_games`, `ci_skip`, `chromium_only`, and `desktop_only`. `--strict-markers` is on, so an unknown marker fails collection.

## Devices

`--device` picks the browser profile for the run. The default is `desktop`, which keeps the current viewport (`VIEWPORT_WIDTH` by `VIEWPORT_HEIGHT`, 1280×720 unless you change those variables).

```bash
pytest --device desktop
pytest --device mobile
HEADLESS=true pytest --device mobile -n auto
```

`--device mobile` uses Playwright's built-in iPhone 14 descriptor: viewport, user agent, and touch. Chromium and WebKit also set `is_mobile`. Firefox omits `is_mobile`, which that browser does not accept.

`desktop_only` marks a test that checks the desktop site: the top nav, the All menu, the numbered search-page strip, the desktop footer, or the desktop sign-in screenshot. With `--device mobile`, those tests are skipped. Cart, sign-in, and language settings still run. The mobile header uses its own search box and Sign in link, and language settings open from the footer. The marker is registered in `pytest.ini`.

## Continuous Integration

[`.github/workflows/run-tests.yml`](.github/workflows/run-tests.yml) runs on every push to `main`, on pull requests, every day at 13:00 UTC (`0 13 * * *`), and when the workflow is started by hand. The workflow uses `ubuntu-latest` and Python 3.12, caches pip, and installs `requirements.txt`.

The test job is a matrix over `chromium`, `firefox`, and `webkit` with `fail-fast: false`, so one browser does not cancel the others. Each job installs only that browser, with its system libraries (`playwright install --with-deps`). It sets `HEADLESS=true`, `SLOW_MO=0`, `BROWSER` to the matrix value, and an empty `BROWSER_CHANNEL` so Chromium is the Playwright build rather than installed Google Chrome. The other variables in `.env.example` (`BASE_URL`, `DEFAULT_TIMEOUT_MS`, `VIEWPORT_WIDTH`, `VIEWPORT_HEIGHT`) are set to those sample values. Pull requests run `pytest -n auto --reruns 1 tests/test_sell.py tests/test_login.py::test_invalid_login`. Pushes to `main`, the daily schedule, and manual runs keep `pytest -n auto -m "not ci_skip" --reruns 1`. The extra retry covers a dropped connection. It does not change what a test asserts.

`ci_skip` is for a test that cannot pass on a GitHub-hosted runner. Right now that is only `tests/test_automotive.py::test_add_2023_tesla_model_3_to_garage`: the Your Garage year/make/model control does not open in headless Chromium. It is deselected on every browser. CI keeps the default `--device desktop`.

`chromium_only` is for the sign-in pixel check. The baseline image is Chromium. Firefox and WebKit skip that test instead of comparing against a screenshot they cannot match.

Each job uploads `reports/` as `reports-chromium`, `reports-firefox`, or `reports-webkit`, including when tests fail. Open the workflow run on GitHub and download the artifact for that browser. It contains `report.html` and `pytest-debug.html`.

When a job fails, it also uploads `test-results/traces` as `traces-chromium`, `traces-firefox`, or `traces-webkit`.

## Reports

`reports/` is gitignored. A run writes:

- `reports/report.html` — plain-language cards (title, steps, outcome, and the error). A failed test includes a page screenshot when the browser can still capture one.
- `reports/pytest-debug.html` — pytest-html output configured in `pytest.ini`.

The automotive test also saves `reports/seat_covers_added_to_cart.png` and `reports/seat_covers_cart.png`.

On a visual mismatch, `utils/visual.py` writes `reports/amazon_login_form_actual.png` and `reports/amazon_login_form_diff.png`. If the baseline file is missing, that run saves the current screenshot as the baseline. Under `pytest -n`, those files include the worker id.

## Traces

A failure writes `test-results/traces/<test-name>.<worker-id>.zip`. The trace includes screenshots, DOM snapshots, and the test sources. A pass discards the trace, so no zip is left behind. `test-results/` is gitignored.

With `pytest -n`, the worker id is the xdist name (`gw0`, `gw1`, ...), for example `test_invalid_login.gw0.zip`. A run without `-n` uses `local`, for example `test_invalid_login.local.zip`.

Open the zip at https://trace.playwright.dev. Drag the file onto the page. The viewer shows each action, the page snapshot, and the source line.

Author: Abidur Chowdhury, [abidur.net](https://abidur.net)
