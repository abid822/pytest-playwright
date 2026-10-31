import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_BROWSERS = ("chromium", "firefox", "webkit")
DEVICES = ("desktop", "mobile")
# Playwright's built-in descriptor. Firefox does not accept is_mobile.
MOBILE_PLAYWRIGHT_DEVICE = "iPhone 14"


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _browser() -> str:
    raw = (os.getenv("BROWSER") or "chromium").strip().lower()
    if raw not in _BROWSERS:
        allowed = ", ".join(_BROWSERS)
        raise ValueError(f"BROWSER must be one of {allowed} (got {raw!r}).")
    return raw


def report_png(stem: str) -> Path:
    """Report image path. Parallel workers each get their own file."""
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    worker = os.environ.get("PYTEST_XDIST_WORKER", "").strip()
    filename = f"{stem}.{worker}.png" if worker else f"{stem}.png"
    return reports / filename


def normalize_device(raw: str | None) -> str:
    """`--device` value. Default is desktop."""
    device = (raw or "desktop").strip().lower()
    if device not in DEVICES:
        allowed = ", ".join(DEVICES)
        raise ValueError(f"--device must be one of {allowed} (got {raw!r}).")
    return device


class Settings:
    base_url: str = os.getenv("BASE_URL", "https://www.amazon.com/")
    browser: str = _browser()
    # Used only when browser is chromium. Empty uses Playwright's Chromium.
    browser_channel: str = os.getenv("BROWSER_CHANNEL", "chrome")
    headless: bool = _bool("HEADLESS", False)
    slow_mo: int = int(os.getenv("SLOW_MO", "0" if _bool("HEADLESS", False) else "250"))
    default_timeout_ms: int = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
    viewport_width: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    viewport_height: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))
    # Set from the --device pytest option in conftest.py. Default stays desktop.
    device: str = "desktop"


settings = Settings()


def browser_context_options(
    device: str,
    browser: str,
    playwright_devices: dict | None = None,
) -> dict:
    """Context options for `--device`.

    Desktop keeps the configured viewport (1280x720 unless overridden).
    Mobile copies viewport, user agent, touch, and is_mobile from Playwright's
    iPhone 14 descriptor. Firefox omits is_mobile.
    """
    chosen = normalize_device(device)
    if chosen == "desktop":
        return {
            "viewport": {
                "width": settings.viewport_width,
                "height": settings.viewport_height,
            }
        }
    if not playwright_devices or MOBILE_PLAYWRIGHT_DEVICE not in playwright_devices:
        raise ValueError(
            f"Playwright has no built-in device {MOBILE_PLAYWRIGHT_DEVICE!r}."
        )
    descriptor = playwright_devices[MOBILE_PLAYWRIGHT_DEVICE]
    options = {
        "viewport": {
            "width": descriptor["viewport"]["width"],
            "height": descriptor["viewport"]["height"],
        },
        "user_agent": descriptor["user_agent"],
        "has_touch": descriptor["has_touch"],
    }
    if browser != "firefox":
        options["is_mobile"] = descriptor["is_mobile"]
    return options
