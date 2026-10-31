import base64

import pytest
from playwright.sync_api import expect, sync_playwright

from config.settings import ROOT, settings
from pages.automotive_page import AutomotivePage
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


@pytest.fixture(scope="session")
def browser_context_managed():
    (ROOT / "reports").mkdir(exist_ok=True)
    launch_args = {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
        "args": ["--disable-blink-features=AutomationControlled"],
    }
    if settings.browser_channel:
        launch_args["channel"] = settings.browser_channel

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_args)
        context = browser.new_context(
            viewport={
                "width": settings.viewport_width,
                "height": settings.viewport_height,
            },
            ignore_https_errors=True,
        )
        context.set_default_timeout(settings.default_timeout_ms)
        expect.set_options(timeout=settings.default_timeout_ms)
        yield context
        context.close()
        browser.close()


@pytest.fixture
def sb_page(browser_context_managed, request):
    page = browser_context_managed.new_page()
    request.node.page = page
    yield page
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


def pytest_configure(config):
    (ROOT / "reports").mkdir(exist_ok=True)
    config._friendly_report = ReportCollector()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
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
    collector = getattr(item.config, "_friendly_report", None)
    if collector is None:
        return
    file_name = ""
    if item.fspath:
        file_name = str(item.fspath.basename)
    collector.add(
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


def pytest_sessionfinish(session, exitstatus):
    collector = getattr(session.config, "_friendly_report", None)
    if collector is None:
        return
    write_report(collector, ROOT / "reports" / "report.html")
