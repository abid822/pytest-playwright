import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    base_url: str = os.getenv("BASE_URL", "https://www.amazon.com/")
    browser_channel: str = os.getenv("BROWSER_CHANNEL", "chrome")
    headless: bool = _bool("HEADLESS", False)
    slow_mo: int = int(os.getenv("SLOW_MO", "0" if _bool("HEADLESS", False) else "250"))
    default_timeout_ms: int = int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
    viewport_width: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    viewport_height: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))


settings = Settings()
