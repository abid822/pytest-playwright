import re

from playwright.sync_api import expect

from locators.books_locators import BooksLocators
from pages.base_page import BasePage

# Headings that stay on the Books store. The book rows under them rotate.
SHOP_SECTIONS = [
    "What everyone's reading",
    "Discover something new",
    "Explore top categories",
]


class BooksPage(BasePage):
    """Amazon Books: store sections, then a priced Literature & Fiction book."""

    def _books_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Explore top categories$", re.I)
        )

    def _books_ready(self) -> bool:
        # The document title is sometimes blank. The category heading is the check.
        heading = self._books_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_books(self) -> None:
        # Step 1: Open the Books store.
        # The first response is sometimes a shell with no heading.
        self.open(BooksLocators.URL)
        if not self._books_ready():
            self.page.goto(BooksLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Books store is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"/amz-books/store", re.I))
        expect(self.page).to_have_title(re.compile(r"Books", re.I))
        expect(self._books_heading().first).to_be_visible()

    def expect_shop_sections(self, names: list[str] | None = None) -> None:
        # Each store heading is on the landing page.
        missing = []
        for name in names or SHOP_SECTIONS:
            heading = self.page.get_by_role(
                "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
            )
            if heading.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Books sections: {missing}"
