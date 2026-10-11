import re

from playwright.sync_api import Page, expect

from locators.amazon_locators import AmazonSearchLocators
from locators.amazon_tabs_locator import AmazonTabsLocator
from pages.base_page import BasePage

# Tabs we always expect on the top nav (Amazon hides others by region)
CORE_TABS = [
    "Best Sellers",
    "Today's Deals",
    "Prime",
    "Sell",
]


class HomePage(BasePage):
    """Amazon home: search, top nav, hamburger menu, cart badge."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Search box in the header
        self.search_input = page.locator(AmazonSearchLocators.SEARCH_INPUT)
        self.search_button = page.locator(AmazonSearchLocators.SEARCH_BUTTON)
        # Top navigation strip (Best Sellers, Prime, ...)
        self.nav_container = page.locator(AmazonTabsLocator.NAV_CONTAINER)
        self.tab_links = page.locator(AmazonTabsLocator.ALL_TABS_LINKS)
        # All / hamburger button that opens the left menu
        self.hamburger = page.get_by_role(
            "button", name=re.compile(r"Open All Categories Menu", re.I)
        ).or_(page.locator(AmazonTabsLocator.HAMBURGER_MENU))
        # Links inside the open hamburger dialog
        self.menu_items = page.get_by_role("dialog").locator(AmazonTabsLocator.MENU_ITEMS)
        # Cart count in the header
        self.cart_count = page.locator("#nav-cart-count")

    def open_home(self) -> None:
        # Step 1: Load Amazon home
        self.open()
        # Step 2: Wait until search is ready
        expect(self.search_input).to_be_visible()

    def search(self, query: str) -> None:
        # Step 1: Type in the header search box
        expect(self.search_input).to_be_visible()
        self.search_input.fill(query)
        # Step 2: Submit search
        self.search_button.click()
        # Step 3: Wait for results URL
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
        # Step 1: Click All / hamburger
        expect(self.hamburger.first).to_be_visible()
        self.hamburger.first.click()
        # Step 2: Wait for the left menu dialog
        expect(self.page.get_by_role("dialog").locator("#hmenu-content").first).to_be_visible()
        # Step 3: Wait for the first menu link
        expect(self.menu_items.first).to_be_visible()

    def menu_item_texts(self) -> list[str]:
        # Unique labels from the visible hamburger list (same view as the JSON)
        panel = self.visible_hamburger_panel()
        locators = panel.locator("a.hmenu-item")
        texts = []
        seen = set()
        for i in range(locators.count()):
            text = " ".join(locators.nth(i).inner_text().split())
            if text and text not in seen:
                seen.add(text)
                texts.append(text)
        return texts

    def expect_menu_contains(self, expected: list[str]) -> None:
        # Compare live menu to data/hamburger_menu.json
        actual = self.menu_item_texts()
        expected_set = {" ".join(item.split()) for item in expected}
        actual_set = set(actual)

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

        # Still fail if an expected JSON item disappeared from Amazon
        missing = [item for item in expected if " ".join(item.split()) not in actual_set]
        assert not missing, f"Missing hamburger items: {missing}"

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

    def expect_hamburger_menu_scrolled(self, min_scroll_top: int = 40) -> None:
        # scrollTop must have increased after the drag
        metrics = self.hamburger_scroll_metrics()
        assert metrics["scrollTop"] >= min_scroll_top, (
            f"Menu did not scroll; scrollTop={metrics['scrollTop']}"
        )

    def expect_cart_not_empty(self) -> None:
        # Header cart badge should not still be 0
        expect(self.cart_count).not_to_have_text(re.compile(r"^0$"))
