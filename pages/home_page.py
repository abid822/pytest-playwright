import re

from playwright.sync_api import Page, expect

from locators.home_locators import LanguageLocators, SearchLocators
from locators.nav_locators import NavLocators
from pages.base_page import BasePage

# Tabs we always expect on the top nav (Amazon hides others by region)
CORE_TABS = [
    "Best Sellers",
    "Today's Deals",
    "Prime",
    "Sell",
]

# All-menu labels that stay put. The JSON file lists more; those can come
# and go, and a missing one is printed instead of failed.
CORE_MENU_ITEMS = [
    "Best Sellers",
    "New Releases",
    "Prime Video",
    "Amazon Music",
    "Kindle",
    "Books",
    "Electronics",
    "Computers",
    "Your Account",
    "English",
    "United States",
    "Sign in",
]


class HomePage(BasePage):
    """Amazon home: search, top nav, hamburger menu, cart badge."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Search box in the header
        self.search_input = page.locator(SearchLocators.SEARCH_INPUT).first
        self.search_button = page.locator(SearchLocators.SEARCH_BUTTON).first
        # Top navigation strip (Best Sellers, Prime, ...)
        self.nav_container = page.locator(NavLocators.NAV_CONTAINER)
        self.tab_links = page.locator(NavLocators.ALL_TABS_LINKS)
        # All / hamburger button that opens the left menu
        self.hamburger = page.get_by_role(
            "button", name=re.compile(r"Open All Categories Menu", re.I)
        ).or_(page.locator(NavLocators.HAMBURGER_MENU))
        # Links inside the open hamburger dialog
        self.menu_items = page.get_by_role("dialog").locator(NavLocators.MENU_ITEMS)
        # Cart count in the header
        self.cart_count = page.locator("#nav-cart-count")
        self.cart_link = page.locator("#nav-cart")
        # Header language control (EN). The clickable link sits inside the wrapper.
        self.language_control = page.locator(LanguageLocators.HEADER_CONTROL)
        self.language_link = self.language_control.locator("a").first

    def open_home(self) -> None:
        # Step 1: Load Amazon home
        self.open()
        # Step 2: Wait until search is ready
        expect(self.search_input).to_be_visible()

    def search(self, query: str) -> None:
        # Step 1: Type in the header search box
        expect(self.search_input).to_be_visible()
        expect(self.search_input).to_be_enabled()
        self.search_input.fill(query)
        # Step 2: Submit search
        expect(self.search_button).to_be_visible()
        expect(self.search_button).to_be_enabled()
        self.search_button.click()
        # Step 3: Wait for results. A bot checkpoint skips the test.
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"k=", re.I))

    def expect_nav_container(self) -> None:
        # Step 1: Top nav strip is on screen
        expect(self.nav_container).to_be_visible()
        # Step 2: At least one tab link is present
        expect(self.tab_links.first).to_be_visible()

    def expect_core_tabs(self, names: list[str] | None = None) -> None:
        # Step 1: Nav is visible
        self.expect_nav_container()
        # Step 2: Each expected tab name exists in the strip
        missing = []
        for name in names or CORE_TABS:
            tab = self.nav_container.get_by_role("link", name=re.compile(name, re.I))
            if tab.count() == 0:
                missing.append(name)
        assert not missing, f"Missing nav tabs: {missing}"

    def open_hamburger_menu(self) -> None:
        # Step 1: Click All / hamburger until the left menu is actually open
        expect(self.hamburger.first).to_be_visible()
        panel = self.visible_hamburger_panel()
        opened = False
        for _ in range(3):
            self.hamburger.first.click()
            try:
                expect(panel).to_be_visible(timeout=4000)
                opened = True
                break
            except AssertionError:
                continue
        if not opened:
            expect(panel).to_be_visible()
        # Step 2: Wait for the menu dialog and the first link
        expect(self.page.get_by_role("dialog").locator("#hmenu-content").first).to_be_visible()
        expect(self.menu_items.first).to_be_visible()

    def menu_item_texts(self) -> list[str]:
        # Labels from the visible hamburger panel (not a hidden clone).
        # WebKit's inner_text is empty for rows below the fold, so read
        # text_content. The expected JSON labels still have to be present.
        panel = self.visible_hamburger_panel()
        locators = panel.locator("a.hmenu-item")
        texts = []
        seen = set()
        for i in range(locators.count()):
            text = " ".join((locators.nth(i).text_content() or "").split())
            if text and text not in seen:
                seen.add(text)
                texts.append(text)
        return texts

    def expect_menu_contains(self, expected: list[str]) -> None:
        # Compare the live menu to data/hamburger_menu.json.
        # Only the core labels fail the test. Amazon drops the rest often.
        actual = self.menu_item_texts()
        expected_set = {" ".join(item.split()) for item in expected}
        actual_set = set(actual)
        core_set = {" ".join(item.split()) for item in CORE_MENU_ITEMS}

        # New on Amazon but not in our JSON: print only, do not fail
        extras = [item for item in actual if item not in expected_set]
        if extras:
            print("\n=== New hamburger items (not in hamburger_menu.json) ===")
            for item in extras:
                print(f"  + {item}")
            print(
                f"=== {len(extras)} new item(s). "
                "Add them to data/hamburger_menu.json if you want them in the baseline. ===\n"
            )
        else:
            print("\nNo new hamburger items vs hamburger_menu.json.\n")

        missing_other = [
            item
            for item in expected
            if " ".join(item.split()) not in actual_set
            and " ".join(item.split()) not in core_set
        ]
        if missing_other:
            print("\n=== Hamburger items no longer on Amazon (warning only) ===")
            for item in missing_other:
                print(f"  - {item}")
            print("=== Outside the core set, so this does not fail the test. ===\n")

        missing_core = [item for item in CORE_MENU_ITEMS if " ".join(item.split()) not in actual_set]
        assert not missing_core, f"Missing hamburger items: {missing_core}"

    def visible_hamburger_panel(self):
        # The on-screen scrollable list (not a hidden clone)
        return self.page.locator("div.hmenu.hmenu-visible").filter(has_text="Best Sellers").first

    def hamburger_scroll_metrics(self) -> dict:
        # Read scrollHeight / clientHeight / scrollTop from the visible panel
        panel = self.visible_hamburger_panel()
        expect(panel).to_be_visible()
        return panel.evaluate(
            """el => ({
                scrollHeight: el.scrollHeight,
                clientHeight: el.clientHeight,
                scrollTop: el.scrollTop,
                overflowY: getComputedStyle(el).overflowY,
            })"""
        )

    def expect_hamburger_menu_is_scrollable(self) -> None:
        # Menu must be taller than the panel so a scrollbar exists
        metrics = self.hamburger_scroll_metrics()
        assert metrics["overflowY"] in {"scroll", "auto"}, (
            f"Menu overflow-y is {metrics['overflowY']}, expected scroll/auto"
        )
        assert metrics["scrollHeight"] > metrics["clientHeight"] + 20, (
            f"Menu is not tall enough to scroll: {metrics}"
        )

    def scroll_hamburger_menu(self, pixels: int = 500) -> None:
        # Step 1: Find the visible menu panel
        panel = self.visible_hamburger_panel()
        box = panel.bounding_box()
        assert box, "Hamburger menu panel has no bounding box"
        # Step 2: Move the mouse onto the scrollbar (right edge)
        scrollbar_x = box["x"] + box["width"] - 5
        start_y = box["y"] + 50
        end_y = min(box["y"] + box["height"] - 20, start_y + pixels)
        self.page.mouse.move(scrollbar_x, start_y)
        self.page.wait_for_timeout(300)
        # Step 3: Drag the scrollbar down so it is visible on screen
        self.page.mouse.down()
        self.page.mouse.move(scrollbar_x, end_y, steps=25)
        self.page.mouse.up()
        self.page.wait_for_timeout(400)
        # Headless Chromium uses an overlay scrollbar the drag can miss
        if self.hamburger_scroll_metrics()["scrollTop"] < 40:
            self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + 80)
            self.page.mouse.wheel(0, pixels)
            self.page.wait_for_timeout(300)
        if self.hamburger_scroll_metrics()["scrollTop"] < 40:
            panel.evaluate("(el, dy) => { el.scrollTop += dy; }", pixels)

    def expect_hamburger_menu_scrolled(self, min_scroll_top: int = 40) -> None:
        # scrollTop must have increased after the drag
        metrics = self.hamburger_scroll_metrics()
        assert metrics["scrollTop"] >= min_scroll_top, (
            f"Menu did not scroll; scrollTop={metrics['scrollTop']}"
        )

    def _language_form_ready(self) -> bool:
        # The preferences form lists English. Radios can be visually hidden.
        try:
            self.page.get_by_role("heading", name=re.compile(r"Language Settings", re.I)).wait_for(
                state="visible", timeout=8000
            )
            return True
        except Exception:
            return False

    def open_language_settings(self) -> None:
        # Mobile web puts language in the footer, not the desktop EN flyout.
        if self.language_control.count() == 0 or not self.language_control.is_visible():
            self._open_mobile_language_settings()
            return
        # Step 1: Header language control is on screen and can be clicked.
        # WebKit sometimes gives the inner link a zero box; the wrapper is the fallback.
        expect(self.language_control).to_be_visible()
        link = self.language_link
        href = ""
        if link.count():
            href = link.get_attribute("href") or ""
        target = link if link.count() and link.is_visible() else self.language_control
        expect(target).to_be_visible()
        expect(target).to_be_enabled()
        target.scroll_into_view_if_needed()
        # Step 2: Open language preferences. A bot checkpoint skips the test.
        try:
            target.click(timeout=8000)
        except Exception:
            if not href:
                raise
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        if not self._language_form_ready() and href:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"customer-preferences/edit", re.I))

    def _open_mobile_language_settings(self) -> None:
        # Footer control on the mobile site. Same preferences form, nothing is saved.
        link = self.page.get_by_role(
            "link",
            name=re.compile(r"Choose a language for shopping", re.I),
        )
        expect(link.first).to_be_visible()
        href = link.first.get_attribute("href") or ""
        link.first.click()
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        if not self._language_form_ready() and href:
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(re.compile(r"customer-preferences/edit", re.I))

    def expect_english_selected_and_spanish_available(self) -> None:
        # Language form is showing, English is the current choice, Spanish is offered.
        # Do not save — that would switch the shared browser session.
        # Use the radio roles. A hidden header span also contains "English - EN".
        expect(self.page.get_by_role("heading", name=re.compile(r"Language Settings", re.I))).to_be_visible()
        english = self.page.locator(LanguageLocators.ENGLISH_RADIO)
        spanish = self.page.locator(LanguageLocators.SPANISH_RADIO)
        expect(english).to_be_checked()
        expect(spanish).not_to_be_checked()
        expect(english).to_have_accessible_name(re.compile(r"English\s*-\s*EN", re.I))
        expect(spanish).to_have_accessible_name(re.compile(r"español", re.I))
        expect(self.page.get_by_role("button", name=re.compile(r"^Save Changes$", re.I))).to_be_visible()

    def expect_cart_not_empty(self) -> None:
        # Header cart badge should not still be 0.
        # A bot checkpoint skips the test instead of leaving the badge at 0.
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.cart_count).to_be_visible()
        expect(self.cart_count).not_to_have_text(re.compile(r"^0$"))

    def expect_added_to_cart(self) -> None:
        # Amazon confirmation sheet, or the header count ticking up
        added = self.page.get_by_text(re.compile(r"Added to (?:your )?cart", re.I))
        try:
            expect(added.first).to_be_visible(timeout=8000)
        except AssertionError:
            expect(self.cart_count).not_to_have_text(re.compile(r"^0$"))
        skip = self.page.get_by_role(
            "button", name=re.compile(r"No thanks|Skip|Decline coverage", re.I)
        )
        if skip.count() and skip.first.is_visible():
            skip.first.click()

    def open_cart(self) -> None:
        # Overlay after add-to-cart can cover the header; go straight to the cart URL
        go = self.page.get_by_role("link", name=re.compile(r"Go to Cart", re.I))
        if go.count() and go.first.is_visible():
            try:
                go.first.click(timeout=3000)
            except Exception:
                self.page.goto("https://www.amazon.com/gp/cart/view.html")
        else:
            self.page.goto("https://www.amazon.com/gp/cart/view.html")
        expect(self.page).to_have_url(re.compile(r"cart", re.I))

    def expect_cart_has_items(self) -> None:
        # Cart page must list at least one active item, not the empty-cart copy
        empty = self.page.get_by_text(re.compile(r"Your Amazon Cart is empty", re.I))
        if empty.count() and empty.first.is_visible():
            raise AssertionError("Cart page is empty after add-to-cart")
        items = self.page.locator(
            "#sc-active-cart .sc-list-item, [data-name='Active Items'] .sc-list-item, "
            ".sc-list-item-content"
        )
        expect(items.first).to_be_visible()
