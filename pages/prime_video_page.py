import re

from playwright.sync_api import Page, expect

from locators.prime_video_locators import PrimeVideoLocators
from pages.base_page import BasePage


class PrimeVideoPage(BasePage):
    """Amazon Prime Video: storefront carousels, then a title card."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.carousel_titles = page.locator(PrimeVideoLocators.CAROUSEL_TITLE)
        self.title_links = page.locator(PrimeVideoLocators.TITLE_LINK)

    def _prime_video_ready(self) -> bool:
        # The store title says Prime Video, and a carousel row has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Prime Video", title, re.I):
                return False
            return (
                self.carousel_titles.count() > 0
                and self.carousel_titles.first.is_visible()
            )
        except Exception:
            return False

    def open_prime_video(self) -> None:
        # Step 1: Open the Prime Video storefront.
        # The first response is sometimes a shell with no rows.
        self.open(PrimeVideoLocators.URL)
        for _ in range(2):
            if self._prime_video_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Prime Video store is showing, not a bot checkpoint.
        expect(self.page).to_have_url(re.compile(r"/gp/video/storefront", re.I))
        self.expect_title(re.compile(r"Prime Video", re.I))
        expect(self.carousel_titles.first).to_be_visible()

    def expect_carousel(self) -> None:
        # A storefront row has a heading. The row name changes between visits.
        expect(self.carousel_titles.first).to_be_visible()
        text = " ".join((self.carousel_titles.first.text_content() or "").split())
        assert re.search(r"[A-Za-z]", text), f"Prime Video carousel has no heading: {text!r}"

    def expect_title_card(self) -> None:
        # A movie or show card links to a title page and shows a name.
        link = self.title_links.first
        expect(link).to_be_visible()
        image = link.locator("img[alt]")
        alt = ""
        if image.count():
            alt = " ".join((image.first.get_attribute("alt") or "").split())
        label = " ".join((link.get_attribute("aria-label") or "").split())
        text = " ".join((link.inner_text() or "").split())
        name = alt or label or text
        assert re.search(r"[A-Za-z]", name), f"Prime Video title card has no name: {name!r}"
