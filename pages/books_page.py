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

# Genre tiles that stay under Explore top categories.
CATEGORIES = [
    "Romance",
    "Children's Books",
    "Mystery, Thriller & Suspense",
    "Science Fiction & Fantasy",
    "Literature & Fiction",
    "History",
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

    def _category_link(self, name: str):
        # Tile text lives in the link's shadow root. The accessible name has
        # extra whitespace, so match the label instead of anchoring it.
        return self.page.locator(BooksLocators.GENRE_LIST).locator(
            BooksLocators.GENRE_LINK
        ).filter(has_text=re.compile(re.escape(name), re.I)).first

    def expect_categories(self, names: list[str] | None = None) -> None:
        # Step 1: The genre list is on screen
        expect(self.page.locator(BooksLocators.GENRE_LIST)).to_be_visible()
        # Step 2: Each core category is listed
        missing = []
        for name in names or CATEGORIES:
            if self._category_link(name).count() == 0:
                missing.append(name)
        assert not missing, f"Missing Books categories: {missing}"

    def open_category(self, name: str) -> None:
        # Step 1: Open that category from Explore top categories.
        # A tile click can stay put, so follow the href in this tab.
        link = self._category_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        node = re.search(r"node=(\d+)", href)
        assert node, f"{name} category link has no node: {href}"
        if href.startswith("/"):
            href = "https://www.amazon.com" + href
        self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # Step 2: That category is showing
        expect(self.page).to_have_url(re.compile(rf"node={node.group(1)}(?:&|$)"))
        expect(self.page).to_have_title(re.compile(re.escape(name), re.I))
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(re.escape(name), re.I)
            ).first
        ).to_be_visible()

    def expect_priced_book(self) -> None:
        # A book card names the title and shows a dollar price.
        card = self.page.locator(BooksLocators.BOOK).filter(
            has_text=re.compile(r"\$\s*\d")
        ).first
        card.scroll_into_view_if_needed()
        expect(card).to_be_visible()
        title = card.locator(BooksLocators.BOOK_TITLE).first
        expect(title).to_have_attribute(
            "aria-label", re.compile(r"[A-Za-z]{3}")
        )
        label = title.get_attribute("aria-label") or ""
        assert re.search(r"[A-Za-z]{3}", label), f"Book has no title: {label!r}"
        price = card.locator(BooksLocators.BOOK_PRICE).first
        expect(price).to_contain_text(re.compile(r"\$\s*\d"))
