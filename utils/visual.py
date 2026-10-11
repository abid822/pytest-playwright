from pathlib import Path

from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch

from config.settings import ROOT


def compare_screenshot(page, relative_baseline: str, locator=None) -> None:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    baseline = ROOT / relative_baseline
    baseline.parent.mkdir(parents=True, exist_ok=True)
    actual = reports / f"{baseline.stem}_actual.png"
    diff = reports / f"{baseline.stem}_diff.png"

    target = locator if locator is not None else page
    target.screenshot(path=str(actual))

    if not baseline.exists():
        target.screenshot(path=str(baseline))
        return

    img_baseline = Image.open(baseline)
    img_actual = Image.open(actual)
    if img_baseline.size != img_actual.size:
        raise AssertionError(
            f"Screenshot size mismatch: baseline {img_baseline.size} vs actual {img_actual.size}. "
            f"Delete {baseline} to recapture at the current viewport."
        )

    img_diff = Image.new("RGBA", img_baseline.size)
    mismatched = pixelmatch(
        img_baseline, img_actual, img_diff, threshold=0.2, includeAA=True
    )
    if mismatched > 0:
        img_diff.save(diff)
        raise AssertionError(
            f"Visual mismatch: {mismatched} pixels differ. See {diff}"
        )
