import base64
import os
import re
from dataclasses import asdict

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import expect, sync_playwright

from config.settings import (
    ROOT,
    browser_context_options,
    normalize_device,
    settings,
)
from pages.automotive_page import AutomotivePage
from pages.bestsellers_page import BestSellersPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from utils.friendly_report import (
    ReportCollector,
    TestRecord,
    human_title,
    marker_labels,
    readable_error,
    steps_from_item,
    story_why,
    write_report,
)


def _launch_browser(playwright):
    # Each xdist worker is its own process, so this session fixture is one
    # browser per worker. Chromium flags and BROWSER_CHANNEL do not apply
    # to Firefox or WebKit.
    launch_args = {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }
    if settings.browser == "chromium":
        launch_args["args"] = ["--disable-blink-features=AutomationControlled"]
        if settings.browser_channel:
            launch_args["channel"] = settings.browser_channel
    browser_type = getattr(playwright, settings.browser)
    return browser_type.launch(**launch_args)


def _context_options(playwright) -> dict:
    options = browser_context_options(
        settings.device,
        settings.browser,
        playwright.devices,
    )
    options["ignore_https_errors"] = True
    return options


_TRACE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


def _trace_zip(test_name: str):
    """test-results/traces/<test-name>.<worker-id>.zip. xdist-safe."""
    worker = os.environ.get("PYTEST_XDIST_WORKER", "").strip() or "local"
    safe = _TRACE_NAME.sub("_", test_name).strip("._") or "test"
    return ROOT / "test-results" / "traces" / f"{safe}.{worker}.zip"


def _start_tracing(context) -> None:
    # A leftover trace from an interrupted test would make start() fail.
    try:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    except PlaywrightError:
        context.tracing.stop()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)


def _stop_tracing(context, test_name: str, *, failed: bool) -> None:
    path = _trace_zip(test_name)
    if failed:
        path.parent.mkdir(parents=True, exist_ok=True)
        context.tracing.stop(path=path)
        return
    try:
        context.tracing.stop()
    except PlaywrightError:
        return
    if path.is_file():
        path.unlink()


def _outcome_failed(node) -> bool:
    for phase in ("setup", "call"):
        report = getattr(node, f"rep_{phase}", None)
        if report is not None and report.failed:
            return True
    return False


@pytest.fixture(scope="session")
def browser_context_managed():
    (ROOT / "reports").mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = _launch_browser(playwright)
        context = browser.new_context(**_context_options(playwright))
        context.set_default_timeout(settings.default_timeout_ms)
        expect.set_options(timeout=settings.default_timeout_ms)
        yield context
        context.close()
        browser.close()


@pytest.fixture
def sb_page(browser_context_managed, request):
    context = browser_context_managed
    _start_tracing(context)
    page = context.new_page()
    request.node.page = page
    try:
        yield page
    finally:
        try:
            _stop_tracing(
                context,
                request.node.name,
                failed=_outcome_failed(request.node),
            )
        finally:
            page.close()


@pytest.fixture
def home_page(sb_page) -> HomePage:
    return HomePage(sb_page)


@pytest.fixture
def login_page(sb_page) -> LoginPage:
    return LoginPage(sb_page)


@pytest.fixture
def search_results_page(sb_page) -> SearchResultsPage:
    return SearchResultsPage(sb_page)


@pytest.fixture
def automotive_page(sb_page) -> AutomotivePage:
    return AutomotivePage(sb_page)


@pytest.fixture
def bestsellers_page(sb_page) -> BestSellersPage:
    return BestSellersPage(sb_page)


# Workers record results on the pytest report. The controller (or a run
# without xdist) copies those onto one collector and writes report.html.
_friendly_collector: ReportCollector | None = None
_is_xdist_worker = False


def pytest_addoption(parser):
    parser.addoption(
        "--device",
        default="desktop",
        help="Device profile: desktop (1280x720) or mobile (iPhone 14).",
    )


def pytest_configure(config):
    global _friendly_collector, _is_xdist_worker
    try:
        settings.device = normalize_device(config.getoption("--device"))
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    (ROOT / "reports").mkdir(exist_ok=True)
    _is_xdist_worker = hasattr(config, "workerinput")
    _friendly_collector = ReportCollector()
    config._friendly_report = _friendly_collector


def pytest_collection_modifyitems(config, items):
    if normalize_device(config.getoption("--device")) != "mobile":
        return
    skip = pytest.mark.skip(
        reason="desktop-only test does not run with --device mobile"
    )
    for item in items:
        if item.get_closest_marker("desktop_only"):
            item.add_marker(skip)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    extras = getattr(report, "extras", [])
    screenshot_b64 = ""
    page = getattr(item, "page", None)
    if report.when == "call" and report.failed and page:
        try:
            screenshot_bytes = page.screenshot(timeout=5000)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        except Exception:
            screenshot_b64 = ""
        else:
            try:
                import pytest_html

                extras.append(
                    pytest_html.extras.html(
                        f'<div><img src="data:image/png;base64,{screenshot_b64}" '
                        f'alt="screenshot" style="width:600px;border:2px solid red;" /></div>'
                    )
                )
            except Exception:
                pass
    report.extras = extras

    if report.when != "call":
        return
    file_name = ""
    if item.fspath:
        file_name = str(item.fspath.basename)
    # Travels with the report to the xdist controller. A worker-local list
    # would be dropped when that process exits.
    report.friendly_record = asdict(
        TestRecord(
            nodeid=item.nodeid,
            name=item.name,
            title=human_title(item.name),
            why=story_why(item),
            steps=steps_from_item(item),
            markers=marker_labels(item),
            outcome=report.outcome,
            duration_s=report.duration,
            stdout=report.capstdout or "",
            error=readable_error(report.longrepr) if report.failed else "",
            screenshot_b64=screenshot_b64,
            file_name=file_name,
        )
    )


def pytest_runtest_logreport(report):
    if _is_xdist_worker or _friendly_collector is None:
        return
    payload = getattr(report, "friendly_record", None)
    if not isinstance(payload, dict):
        return
    _friendly_collector.add(TestRecord(**payload))


def pytest_sessionfinish(session, exitstatus):
    if _is_xdist_worker or _friendly_collector is None:
        return
    _friendly_collector.records.sort(key=lambda record: record.nodeid)
    write_report(
        _friendly_collector,
        ROOT / "reports" / "report.html",
        browser=settings.browser,
    )
