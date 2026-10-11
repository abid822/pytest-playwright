import re

from playwright.sync_api import Page, expect

from config.settings import settings


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, url: str | None = None) -> None:
        self.page.goto(url or settings.base_url)
        expect(self.page).to_have_url(re.compile(r"amazon\.com", re.I))
