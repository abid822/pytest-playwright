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

# Home sometimes ships a short legal card instead of the four columns.
COMPACT_LINKS = [
    "Customer Service",
    "About Amazon",
    "Conditions of Use",
    "Privacy Notice",
]


class FooterPage(BasePage):
    """Amazon footer: column headings, help links, and Back to top."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.footer = page.locator(FooterLocators.FOOTER)
        # Desktop uses #navBackToTop. Some layouts expose a button or link instead.
        self.back_to_top = page.locator(FooterLocators.BACK_TO_TOP).or_(
            page.get_by_role("button", name=re.compile(r"^Back to top$", re.I))
        ).or_(page.get_by_role("link", name=re.compile(r"^Back to top$", re.I)))
        self.search_input = page.locator(SearchLocators.SEARCH_INPUT).first

    def open_home(self) -> None:
        # Step 1: Load Amazon home, then wait until the search box is ready.
        self.open()
        self.wait_for_search_box(self.search_input)

    def _column_heading(self, name: str):
        # Heads are div.navFooterColHead. The heading role is missing until
        # the footer lays out, so match the class and the role.
        pattern = re.compile(rf"^\s*{re.escape(name)}\s*$")
        by_class = self.footer.locator(FooterLocators.COLUMN_HEAD).filter(has_text=pattern)
        by_role = self.footer.get_by_role("heading", name=pattern)
        return by_class.or_(by_role)

    def _compact_card(self):
        return self.footer.locator(".navFooterCardLinks, .navFooterCardContent")

    def footer_kind(self) -> str:
        # Classic columns, or the shorter legal card. Wait until one is in the DOM.
        expect(self.footer).to_be_visible()
        self.footer.scroll_into_view_if_needed()
        classic = self._column_heading(FOOTER_COLUMNS[0])
        card = self._compact_card()
        expect(classic.or_(card).first).to_be_attached()
        if classic.count() > 0:
            return "classic"
        return "compact"

    def expect_compact_footer(self, names: list[str] | None = None) -> None:
        # The short footer has these legal links and no column headings.
        expect(self._compact_card().first).to_be_visible()
        for name in names or COMPACT_LINKS:
            link = self.footer.get_by_role(
                "link", name=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
            )
            expect(link.first).to_be_visible()

    def expect_footer_columns(self, names: list[str] | None = None) -> None:
        # Step 1: The footer is on the page. Headings below the fold are not
        # in the tree until it lays out, so scroll it into view and wait.
        expect(self.footer).to_be_visible()
        self.footer.scroll_into_view_if_needed()
        self.page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        # Step 2: Each column heading is listed
        for name in names or FOOTER_COLUMNS:
            expect(self._column_heading(name).first).to_be_visible()

    def expect_help_links(self, names: list[str] | None = None) -> None:
        # Let Us Help You keeps these links. Other footer links come and go.
        column = self.footer.locator(".navFooterLinkCol").filter(
            has=self.page.locator(FooterLocators.COLUMN_HEAD).filter(
                has_text=re.compile(r"^\s*Let Us Help You\s*$")
            )
        )
        expect(column.first).to_be_visible()
        for name in names or HELP_LINKS:
            link = column.get_by_role(
                "link", name=re.compile(rf"^\s*{re.escape(name)}\s*$")
            )
            expect(link.first).to_be_visible()

    def _back_to_top_control(self):
        return self.back_to_top.locator("visible=true").first

    def has_back_to_top(self) -> bool:
        # The short footer sometimes has no Back to top control.
        self.page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        try:
            self.page.wait_for_function("() => window.scrollY > 200", timeout=4000)
        except Exception:
            pass
        try:
            return self._back_to_top_control().is_visible()
        except Exception:
            return False

    def scroll_to_bottom(self) -> None:
        # Step 1: Move to the bottom so Back to top has somewhere to return from
        self.page.evaluate(
            "() => window.scrollTo(0, document.body.scrollHeight)"
        )
        self.page.wait_for_function("() => window.scrollY > 400", timeout=8000)
        control = self._back_to_top_control()
        control.scroll_into_view_if_needed()
        expect(control).to_be_visible()
        expect(control).to_have_accessible_name(re.compile(r"back to top", re.I))

    def click_back_to_top(self) -> None:
        # Step 1: Click Back to top
        control = self._back_to_top_control()
        expect(control).to_be_visible()
        control.scroll_into_view_if_needed()
        control.click()
        # Step 2: The page is back at the header
        try:
            self.page.wait_for_function("() => window.scrollY < 40", timeout=8000)
        except Exception:
            control.click()
            self.page.wait_for_function("() => window.scrollY < 40", timeout=8000)
        top = self.page.evaluate("() => window.scrollY")
        assert top < 40, f"Back to top left the page at scrollY={top}"
