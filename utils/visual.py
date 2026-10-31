import platform
from pathlib import Path

from PIL import Image, ImageFilter
from pixelmatch.contrib.PIL import pixelmatch

from config.settings import ROOT, report_png

# Soften glyph edges so one baseline can be compared from macOS Chrome and
# headless Chromium. A missing control or a shifted layout is still thousands
# of pixels on the sign-in card (~134k px); this budget is under 1%.
_BLUR_RADIUS = 1.2
_MAX_MISMATCH_RATIO = 0.008


def _baseline_path(relative_baseline: str) -> Path:
    """Prefer a platform file such as amazon_login_form.darwin.png when present."""
    path = ROOT / relative_baseline
    specific = path.with_name(f"{path.stem}.{platform.system().lower()}{path.suffix}")
    if specific.exists():
        return specific
    return path


def compare_screenshot(
    page,
    relative_baseline: str,
    locator=None,
    *,
    max_mismatch_ratio: float = _MAX_MISMATCH_RATIO,
) -> None:
    baseline = _baseline_path(relative_baseline)
    baseline.parent.mkdir(parents=True, exist_ok=True)
    actual = report_png(f"{baseline.stem}_actual")
    diff = report_png(f"{baseline.stem}_diff")

    target = locator if locator is not None else page
    target.screenshot(path=str(actual))

    if not baseline.exists():
        target.screenshot(path=str(baseline))
        return

    img_baseline = Image.open(baseline).convert("RGBA")
    img_actual = Image.open(actual).convert("RGBA")
    if img_baseline.size != img_actual.size:
        raise AssertionError(
            f"Screenshot size mismatch: baseline {img_baseline.size} vs actual {img_actual.size}. "
            f"Delete {baseline} to recapture at the current viewport."
        )

    blur = ImageFilter.GaussianBlur(_BLUR_RADIUS)
    left = img_baseline.filter(blur)
    right = img_actual.filter(blur)
    img_diff = Image.new("RGBA", left.size)
    mismatched = pixelmatch(left, right, img_diff, threshold=0.2, includeAA=True)
    limit = max(40, int(left.size[0] * left.size[1] * max_mismatch_ratio))
    if mismatched > limit:
        img_diff.save(diff)
        raise AssertionError(
            f"Visual mismatch: {mismatched} pixels differ (limit {limit}). See {diff}"
        )
