import re

from playwright.sync_api import Page, expect

from locators.cds_vinyl_locators import CDsVinylLocators
from pages.base_page import BasePage

# Genres that stay in the CDs & Vinyl column. Seasonal tiles rotate.
CORE_GENRES = [
    "Pop",
    "Rock",
    "Jazz",
    "Classical Music",
]


class CDsVinylPage(BasePage):
    """Amazon CDs & Vinyl: store genres, then a priced Rock album."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.browse = page.locator(CDsVinylLocators.BROWSE).first

    def _store_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^CDs & Vinyl$", re.I)
        )

    def _cds_ready(self) -> bool:
        # The store heading says CDs & Vinyl, and the genre column has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"CDs & Vinyl", title, re.I):
                return False
            heading = self._store_heading()
            if heading.count() == 0 or not heading.first.is_visible():
                return False
            return self.browse.count() > 0 and self.browse.is_visible()
        except Exception:
            return False

    def open_cds_vinyl(self) -> None:
        # Step 1: Open the CDs & Vinyl store.
        # The first response is sometimes a shell with no genre column.
        self.open(CDsVinylLocators.URL)
        for _ in range(2):
            if self._cds_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The CDs & Vinyl store is showing, not a bot checkpoint.
        # The document title says "CDs & Vinyl".
        expect(self.page).to_have_url(re.compile(r"node=5174(?:&|$)"))
        self.expect_title(re.compile(r"CDs & Vinyl", re.I))
        expect(self._store_heading().first).to_be_visible()
        expect(self.browse).to_be_visible()

    def _genre_link(self, name: str):
        # Link text includes surrounding whitespace. Match the column label.
        return self.page.locator(CDsVinylLocators.BROWSE_LINK).filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        ).first

    def expect_core_genres(self, names: list[str] | None = None) -> None:
        # Step 1: The genre column is on screen
        expect(self.browse).to_be_visible()
        # Step 2: Each core genre is listed
        missing = []
        for name in names or CORE_GENRES:
            link = self._genre_link(name)
            if link.count() == 0:
                missing.append(name)
        assert not missing, f"Missing CDs & Vinyl genres: {missing}"

    def _genre_heading(self, name: str):
        return self.page.get_by_role(
            "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
        )

    def _genre_ready(self, name: str) -> bool:
        try:
            title = self.page.title() or ""
            if re.search(rf"(?:^|:\s*){re.escape(name)}(?:\s*:|$)", title, re.I):
                return True
            heading = self._genre_heading(name)
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_genre(self, name: str) -> None:
        # Step 1: Open that genre from the store column
        link = self._genre_link(name)
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        match = re.search(r"node=(\d+)", href)
        assert match, f"{name} genre link has no node"
        node = match.group(1)
        link.click()
        # Step 2: If the click does not leave the landing page, follow the href
        try:
            expect(self.page).to_have_url(
                re.compile(rf"node={node}(?:&|$)"), timeout=8000
            )
        except AssertionError:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            assert href, f"{name} genre link has no href"
            self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # The click sometimes lands on a shell: right node, empty title, no prices.
        # A reload paints the genre page. A second goto of the same href does not.
        if not self._genre_ready(name):
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(rf"node={node}(?:&|$)"))
        self.expect_title(re.compile(rf"(?:^|:\s*){re.escape(name)}(?:\s*:|$)", re.I))
        heading = self._genre_heading(name)
        if heading.count() > 0:
            expect(heading.first).to_be_visible()

    def expect_priced_product(self) -> None:
        # An album card on the genre page shows a dollar price.
        price = self.page.locator(CDsVinylLocators.PRODUCT_PRICE).first
        expect(price).to_be_attached()
        text = " ".join((price.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), (
            f"CDs & Vinyl album has no price: {text!r}"
        )
