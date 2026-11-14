import re

from playwright.sync_api import Page, expect

from locators.footer_locators import FooterLocators
from locators.home_locators import SearchLocators
from pages.base_page import BasePage

# Column headings that stay in the desktop footer. Link lists under them rotate.
FOOTER_COLUMNS = [
    "Get to Know Us",
    "Make Money with Us",
    "Amazon Payment Products",
    "Let Us Help You",
]

# Links that stay in Let Us Help You.
HELP_LINKS = [
    "Your Account",
    "Your Orders",
    "Shipping Rates & Policies",
    "Help",
]


class FooterPage(BasePage):
    """Amazon footer: column headings, help links, and Back to top."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.footer = page.locator(FooterLocators.FOOTER)
        self.back_to_top = page.locator(FooterLocators.BACK_TO_TOP)
        self.search_input = page.locator(SearchLocators.SEARCH_INPUT).first

    def open_home(self) -> None:
        # Step 1: Load Amazon home, then wait until the search box is ready.
        self.open()
        self.wait_for_search_box(self.search_input)

    def expect_footer_columns(self, names: list[str] | None = None) -> None:
        # Step 1: The footer is on the page. Headings below the fold are not
        # in the tree until it lays out, so scroll it into view and wait.
        expect(self.footer).to_be_visible()
        self.footer.scroll_into_view_if_needed()
        heads = self.footer.locator(FooterLocators.COLUMN_HEAD)
        expect(heads.first).to_be_visible()
        # Step 2: Each column heading is listed
        for name in names or FOOTER_COLUMNS:
            heading = heads.filter(has_text=re.compile(rf"^{re.escape(name)}$"))
            expect(heading.first).to_be_visible()

    def expect_help_links(self, names: list[str] | None = None) -> None:
        # Let Us Help You keeps these links. Other footer links come and go.
        column = self.footer.locator(".navFooterLinkCol").filter(
            has=self.page.locator(FooterLocators.COLUMN_HEAD).filter(
                has_text=re.compile(r"^Let Us Help You$")
            )
        )
        expect(column.first).to_be_visible()
        for name in names or HELP_LINKS:
            link = column.get_by_role(
                "link", name=re.compile(rf"^{re.escape(name)}$")
            )
            expect(link.first).to_be_visible()

    def scroll_to_bottom(self) -> None:
        # Step 1: Move to the bottom so Back to top has somewhere to return from
        self.page.evaluate(
            "() => window.scrollTo(0, document.body.scrollHeight)"
        )
        self.page.wait_for_function("() => window.scrollY > 400", timeout=8000)
        expect(self.back_to_top).to_be_visible()
        expect(self.back_to_top).to_have_attribute(
            "aria-label", re.compile(r"^Back to top$", re.I)
        )

    def click_back_to_top(self) -> None:
        # Step 1: Click Back to top
        expect(self.back_to_top).to_be_visible()
        self.back_to_top.click()
        # Step 2: The page is back at the header
        try:
            self.page.wait_for_function("() => window.scrollY < 40", timeout=8000)
        except Exception:
            self.back_to_top.click()
            self.page.wait_for_function("() => window.scrollY < 40", timeout=8000)
        top = self.page.evaluate("() => window.scrollY")
        assert top < 40, f"Back to top left the page at scrollY={top}"
