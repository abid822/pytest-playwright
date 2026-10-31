import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_BROWSERS = ("chromium", "firefox", "webkit")


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


settings = Settings()
