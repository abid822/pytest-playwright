import base64

import pytest
from playwright.sync_api import expect, sync_playwright

from config.settings import ROOT, settings
from pages.automotive_page import AutomotivePage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage


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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call" and report.failed:
        page = getattr(item, "page", None)
        if page:
            import pytest_html

            screenshot_bytes = page.screenshot()
            b64_img = base64.b64encode(screenshot_bytes).decode()
            extras.append(
                pytest_html.extras.html(
                    f'<div><img src="data:image/png;base64,{b64_img}" '
                    f'alt="screenshot" style="width:600px;border:2px solid red;" /></div>'
                )
            )
    report.extras = extras
