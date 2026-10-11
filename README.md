# pytest-playwright

Pytest + Playwright (Python) UI tests for Amazon, using a page object model.

## Layout

| Path | Role |
| --- | --- |
| `tests/` | Specs only: steps and assertions |
| `pages/` | Actions (click, type, wait) |
| `locators/` | CSS / role selectors |
| `data/` | JSON fixtures (hamburger menu, etc.) |
| `baselines/` | Pixelmatch screenshots |
| `config/settings.py` | Base URL, browser, timeouts |

## Setup

Python 3.11+ recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

`.env` controls headed Chrome so you can watch runs:

- `HEADLESS=false`
- `BROWSER_CHANNEL=chrome`
- `SLOW_MO=250`

## Run tests

```bash
pytest -v
pytest tests/test_amazon_automotive_vehicle.py -v
pytest -m smoke
pytest -m login
pytest -m tabs
pytest -m automotive
```

HTML report: `reports/report.html`

## Markers

- `smoke` — critical path
- `login` — sign-in page
- `cart` — add to cart
- `tabs` — nav tabs and hamburger
- `automotive` — Your Garage + seat-cover search

Amazon is a live site (captcha, geo, A/B). Failures can be environmental, not only product bugs.

## Contributing

Open a pull request against `main`. Do not push commits straight to `main`.
