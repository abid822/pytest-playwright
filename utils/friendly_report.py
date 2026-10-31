"""Self-contained, human-readable HTML report for Amazon UI tests."""

from __future__ import annotations

import html
import inspect
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

STORIES: dict[str, dict[str, str]] = {
    "test_add_2023_tesla_model_3_to_garage": {
        "title": "Tesla garage and cheapest seat covers",
        "why": "Adds a 2023 Tesla Model 3 to Your Garage, searches seat covers, sorts low to high, adds an in-stock item, then opens the cart and screenshots it.",
    },
    "test_add_cheap_cable_to_cart": {
        "title": "Cheap USB-C cable in the cart",
        "why": "Searches for a USB-C charging cable and confirms the header cart is no longer empty.",
    },
    "test_nav_container": {
        "title": "Top navigation is on the page",
        "why": "Opens Amazon home and checks that the header tab strip is visible with more than a few links.",
    },
    "test_nav_hamburger": {
        "title": "All menu list and scrollbar",
        "why": "Opens the hamburger menu, checks the core departments are still there, then drags the scrollbar so Sign in comes into view.",
    },
    "test_nav_tabs": {
        "title": "Core store tabs",
        "why": "Confirms Best Sellers, Today's Deals, Prime, and Sell are in the top nav.",
    },
    "test_invalid_login": {
        "title": "Bad email is rejected",
        "why": "Opens sign-in, submits an email with no @, and expects the error plus helper links.",
    },
    "test_login_form_visual": {
        "title": "Sign-in form still looks the same",
        "why": "Compares the live sign-in card to the baseline screenshot. A fail means Amazon changed the layout.",
    },
    "test_search_results_second_page_lists_different_products": {
        "title": "Search page 2 is a new set of products",
        "why": "Searches hardcover notebooks, notes page 1 titles, opens page 2, and checks the products changed.",
    },
    "test_language_settings_keep_english_and_offer_spanish": {
        "title": "Language settings offer English and Spanish",
        "why": "Opens the header language control and checks that English is selected, Spanish is available, and the choice is not saved.",
    },
}

MARKER_LABELS = {
    "smoke": "Critical path",
    "login": "Sign-in",
    "cart": "Cart",
    "tabs": "Navigation",
    "automotive": "Automotive",
    "search": "Search",
    "language": "Language",
    "ci_skip": "Skipped in CI",
    "chromium_only": "Chromium baseline",
}


@dataclass
class TestRecord:
    nodeid: str
    name: str
    title: str
    why: str
    steps: list[str]
    markers: list[str]
    outcome: str
    duration_s: float
    stdout: str = ""
    error: str = ""
    screenshot_b64: str = ""
    file_name: str = ""


@dataclass
class ReportCollector:
    records: list[TestRecord] = field(default_factory=list)
    started: datetime = field(default_factory=datetime.now)

    def add(self, record: TestRecord) -> None:
        self.records.append(record)


def human_title(name: str) -> str:
    story = STORIES.get(name)
    if story:
        return story["title"]
    label = name[5:] if name.startswith("test_") else name
    return label.replace("_", " ").capitalize()


def story_why(item) -> str:
    doc = (item.obj.__doc__ or "").strip()
    if doc:
        return " ".join(doc.split())
    story = STORIES.get(item.name)
    if story:
        return story["why"]
    return "Automated browser check against live Amazon."


def steps_from_item(item) -> list[str]:
    try:
        source = inspect.getsource(item.obj)
    except OSError:
        return []
    steps: list[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        match = re.match(r"#\s*(Step\s+\d+\s*:.*)", stripped, re.I)
        if match:
            steps.append(match.group(1).strip())
    return steps


def marker_labels(item) -> list[str]:
    labels = []
    for mark in item.iter_markers():
        if mark.name in {"parametrize", "usefixtures", "filterwarnings"}:
            continue
        labels.append(MARKER_LABELS.get(mark.name, mark.name.replace("_", " ").title()))
    # unique, keep order
    seen: set[str] = set()
    out: list[str] = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def readable_error(longrepr) -> str:
    if not longrepr:
        return ""
    text = str(longrepr)
    if "Continue shopping" in text:
        return (
            "Amazon showed a Continue shopping checkpoint instead of the real homepage "
            "(common bot/captcha wall). Retry the run in headed Chrome."
        )
    if "No organic search results found" in text:
        return "Search results loaded, but no non-sponsored product titles could be read."
    if "Visual mismatch" in text:
        match = re.search(r"Visual mismatch: .*", text)
        return match.group(0) if match else "The sign-in form no longer matches the baseline screenshot."
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    for line in reversed(lines):
        stripped = line.lstrip("E ").strip()
        if stripped.startswith(("AssertionError", "TimeoutError", "playwright.", "Error")):
            return stripped[:800]
    return (lines[-1] if lines else text)[:800]


def write_report(collector: ReportCollector, path: Path, *, browser: str = "") -> None:
    path.parent.mkdir(exist_ok=True)
    records = collector.records
    passed = sum(1 for r in records if r.outcome == "passed")
    failed = sum(1 for r in records if r.outcome == "failed")
    skipped = sum(1 for r in records if r.outcome == "skipped")
    other = len(records) - passed - failed - skipped
    duration = sum(r.duration_s for r in records)
    ended = datetime.now()
    pass_pct = round(100 * passed / len(records)) if records else 0

    cards = "\n".join(_test_card(r, i) for i, r in enumerate(records, start=1))
    html_doc = _TEMPLATE.format(
        generated=ended.strftime("%b %d, %Y · %I:%M %p"),
        started=collector.started.strftime("%I:%M %p"),
        total=len(records),
        passed=passed,
        failed=failed,
        skipped=skipped,
        other=other,
        duration=f"{duration:.1f}s",
        pass_pct=pass_pct,
        cards=cards or '<p class="empty">No tests ran.</p>',
        fail_hidden="hidden" if failed == 0 else "",
        browser=html.escape(browser or "chromium"),
    )
    path.write_text(html_doc, encoding="utf-8")


def _test_card(record: TestRecord, index: int) -> str:
    outcome = record.outcome
    status_label = {
        "passed": "Passed",
        "failed": "Failed",
        "skipped": "Skipped",
    }.get(outcome, outcome.title())
    steps = "".join(f"<li>{html.escape(step)}</li>" for step in record.steps) or "<li>No numbered steps in this test.</li>"
    markers = "".join(f'<span class="chip">{html.escape(m)}</span>' for m in record.markers)
    error = ""
    if record.error:
        error = f'<div class="error"><h4>What went wrong</h4><pre>{html.escape(record.error)}</pre></div>'
    shot = ""
    if record.screenshot_b64:
        shot = (
            f'<figure class="shot">'
            f'<img src="data:image/png;base64,{record.screenshot_b64}" alt="Browser at failure"/>'
            f"<figcaption>What the browser showed when this failed</figcaption>"
            f"</figure>"
        )
    log = ""
    if record.stdout.strip():
        log = f'<details class="log"><summary>Test log</summary><pre>{html.escape(record.stdout.strip())}</pre></details>'
    return f"""
<article class="card" data-status="{html.escape(outcome)}">
  <header>
    <span class="index">#{index}</span>
    <span class="badge {html.escape(outcome)}">{html.escape(status_label)}</span>
    <h2>{html.escape(record.title)}</h2>
  </header>
  <p class="why">{html.escape(record.why)}</p>
  <div class="meta">
    {markers}
    <span class="chip quiet">{record.duration_s:.1f}s</span>
    <span class="chip quiet">{html.escape(record.file_name)}</span>
  </div>
  <h3>What we checked</h3>
  <ol class="steps">{steps}</ol>
  {error}
  {shot}
  {log}
</article>
"""


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Amazon UI test report</title>
  <style>
    :root {{
      --bg: #f4f1ea;
      --ink: #1c1914;
      --muted: #5c564c;
      --card: #fffdf8;
      --line: #e4ddd0;
      --pass: #1f7a4d;
      --pass-bg: #e5f6ec;
      --fail: #b42318;
      --fail-bg: #fde8e6;
      --skip: #8a6914;
      --skip-bg: #f8efd2;
      --accent: #c45c26;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", ui-sans-serif, system-ui, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }}
    .hero {{
      background: #1c1914;
      color: #f4f1ea;
      padding: 2.2rem 1.5rem 2rem;
    }}
    .hero h1 {{ margin: 0 0 .35rem; font-size: 1.75rem; letter-spacing: -0.02em; }}
    .hero p {{ margin: 0; color: #d8d0c4; max-width: 42rem; }}
    .wrap {{ max-width: 960px; margin: 0 auto; padding: 0 1.25rem 3rem; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: .75rem;
      margin: -1.4rem 0 1.5rem;
    }}
    .stat {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1rem 1.1rem;
      box-shadow: 0 8px 24px rgba(28,25,20,.06);
    }}
    .stat b {{ display: block; font-size: 1.6rem; }}
    .stat span {{ color: var(--muted); font-size: .85rem; }}
    .stat.pass b {{ color: var(--pass); }}
    .stat.fail b {{ color: var(--fail); }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: .5rem;
      margin-bottom: 1rem;
      align-items: center;
    }}
    .toolbar button {{
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 999px;
      padding: .4rem .9rem;
      cursor: pointer;
      font: inherit;
    }}
    .toolbar button.active {{ background: #1c1914; color: #fffdf8; border-color: #1c1914; }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 1.15rem 1.25rem 1.3rem;
      margin-bottom: 1rem;
    }}
    .card header {{ display: flex; flex-wrap: wrap; gap: .5rem .75rem; align-items: baseline; }}
    .card h2 {{ margin: 0; flex: 1 1 12rem; font-size: 1.15rem; }}
    .index {{ color: var(--muted); font-size: .85rem; }}
    .badge {{
      font-size: .75rem;
      font-weight: 700;
      letter-spacing: .04em;
      text-transform: uppercase;
      padding: .2rem .55rem;
      border-radius: 999px;
    }}
    .badge.passed {{ background: var(--pass-bg); color: var(--pass); }}
    .badge.failed {{ background: var(--fail-bg); color: var(--fail); }}
    .badge.skipped {{ background: var(--skip-bg); color: var(--skip); }}
    .why {{ color: var(--muted); margin: .65rem 0 .8rem; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .8rem; }}
    .chip {{
      font-size: .75rem;
      background: #efe8db;
      border-radius: 999px;
      padding: .15rem .6rem;
    }}
    .chip.quiet {{ background: transparent; border: 1px solid var(--line); color: var(--muted); }}
    h3 {{ font-size: .9rem; margin: .6rem 0 .35rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }}
    .steps {{ margin: 0; padding-left: 1.2rem; }}
    .steps li {{ margin: .2rem 0; }}
    .error {{
      margin-top: 1rem;
      background: var(--fail-bg);
      border-radius: 12px;
      padding: .75rem 1rem;
    }}
    .error h4 {{ margin: 0 0 .4rem; color: var(--fail); }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      margin: 0;
      font-size: .85rem;
    }}
    .shot {{ margin: 1rem 0 0; }}
    .shot img {{
      width: 100%;
      max-width: 720px;
      border-radius: 12px;
      border: 2px solid var(--fail);
    }}
    .shot figcaption {{ color: var(--muted); font-size: .85rem; margin-top: .35rem; }}
    details.log {{ margin-top: .8rem; color: var(--muted); }}
    details.log pre {{ margin-top: .4rem; background: #efe8db; padding: .7rem; border-radius: 10px; }}
    .empty {{ color: var(--muted); }}
    footer {{ color: var(--muted); font-size: .85rem; margin-top: 1.5rem; }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <h1>Amazon UI test report</h1>
      <p>Plain-language results from the pytest-playwright suite. Each card is one customer-facing check on live Amazon.com. Browser: {browser}.</p>
    </div>
  </header>
  <div class="wrap">
    <section class="stats">
      <div class="stat"><b>{total}</b><span>Checks run</span></div>
      <div class="stat pass"><b>{passed}</b><span>Passed</span></div>
      <div class="stat fail"><b>{failed}</b><span>Failed</span></div>
      <div class="stat"><b>{pass_pct}%</b><span>Pass rate</span></div>
      <div class="stat"><b>{duration}</b><span>Browser time · {generated}</span></div>
    </section>
    <div class="toolbar">
      <button type="button" class="active" data-filter="all">All</button>
      <button type="button" data-filter="passed">Passed</button>
      <button type="button" data-filter="failed" {fail_hidden}>Failed</button>
    </div>
    {cards}
    <footer>Generated {generated}. Skipped: {skipped}. Other: {other}. Started {started}.</footer>
  </div>
  <script>
    document.querySelectorAll(".toolbar button").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".toolbar button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const filter = btn.dataset.filter;
        document.querySelectorAll(".card").forEach((card) => {{
          card.style.display = (filter === "all" || card.dataset.status === filter) ? "" : "none";
        }});
      }});
    }});
  </script>
</body>
</html>
"""
