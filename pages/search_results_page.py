import re

from playwright.sync_api import Page, expect

from locators.home_locators import SearchLocators
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    """Search results: sort, paginate, then add a product to the cart."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Each product card in the results grid
        self.results = page.locator(SearchLocators.PRODUCT_CARDS)
        self.sort_select = page.locator(SearchLocators.SORT_SELECT)
        self.selected_page = page.locator(SearchLocators.PAGINATION_SELECTED)

    def sort_by_price_low_to_high(self) -> None:
        # Step 1: Click the visible Sort by control next to the hidden native <select>
        native = self.page.locator("#s-result-sort-select")
        expect(native).to_be_attached()
        visible_sort = native.locator("xpath=following-sibling::span[contains(@class,'a-button')][1]")
        expect(visible_sort).to_be_visible()
        visible_sort.click()
        # Step 2: Choose Price: Low to High from the popover (or the native select)
        popover_option = self.page.locator(".a-popover a, a.a-dropdown-link").filter(
            has_text=re.compile(r"Price:\s*Low to High", re.I)
        )
        try:
            popover_option.first.wait_for(state="visible", timeout=4000)
            popover_option.first.click()
        except Exception:
            native.select_option("price-asc-rank")
        # Step 3: If the widget did not change the URL, follow the option's data-url
        try:
            expect(self.page).to_have_url(re.compile(r"price-asc-rank|s=price-asc"), timeout=8000)
        except AssertionError:
            href = native.locator("option[value='price-asc-rank']").get_attribute("data-url")
            assert href, "Price: Low to High option has no data-url"
            if href.startswith("/"):
                href = "https://www.amazon.com" + href
            self.page.goto(href)
            expect(self.page).to_have_url(re.compile(r"price-asc-rank|s=price-asc"))
        expect(self.results.first).to_be_visible()

    def _dismiss_continue_shopping(self) -> None:
        # Fresh sessions sometimes land on a continue-shopping check
        self.dismiss_continue_shopping()

    def search_from_home(self, query: str) -> None:
        # Step 1: Open Amazon home
        self.open()
        # Step 2: Clear the continue-shopping check when it is shown
        self._dismiss_continue_shopping()
        # Step 3: Type the query and submit
        search = self.page.locator(SearchLocators.SEARCH_INPUT)
        expect(search).to_be_visible()
        search.fill(query)
        self.page.locator(SearchLocators.SEARCH_BUTTON).click()
        # Step 4: Wait until result cards are on the page
        expect(self.page).to_have_url(re.compile(r"[?&]k=", re.I))
        expect(self.results.first).to_be_visible()

    def organic_result_titles(self, limit: int = 3) -> list[str]:
        # First organic titles, skipping sponsored and unavailable tiles
        expect(self.results.first).to_be_visible()
        titles: list[str] = []
        for i in range(min(self.results.count(), 24)):
            card = self.results.nth(i)
            if self._skip_card(card):
                continue
            heading = card.locator(SearchLocators.RESULT_TITLE)
            if heading.count() == 0:
                continue
            text = " ".join(heading.first.inner_text().split())
            if not text:
                continue
            titles.append(text)
            if len(titles) >= limit:
                break
        assert titles, "No organic search results found"
        return titles

    def go_to_results_page(self, number: int) -> None:
        # Step 1: Click the page number in the pagination strip
        link = self.page.locator(SearchLocators.PAGINATION_PAGE_LINK.format(number))
        expect(link).to_be_visible()
        link.scroll_into_view_if_needed()
        link.click()
        # Step 2: URL and the highlighted page number should match
        expect(self.page).to_have_url(re.compile(rf"[?&]page={number}(?:&|$)"))
        expect(self.selected_page).to_have_text(str(number))
        expect(self.results.first).to_be_visible()

    def _skip_card(self, card) -> bool:
        if card.get_by_text(re.compile(r"^Sponsored$")).count() > 0:
            return True
        if card.get_by_text(re.compile(r"Currently unavailable", re.I)).count() > 0:
            return True
        return False

    def _first_shoppable_card(self):
        # Skip Sponsored and out-of-stock tiles; lowest in-stock result is used
        expect(self.results.first).to_be_visible()
        for i in range(min(self.results.count(), 16)):
            card = self.results.nth(i)
            if not self._skip_card(card):
                return card
        return self.results.first

    def _add_from_product_page(self) -> bool:
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        if self.page.get_by_text(re.compile(r"Currently unavailable", re.I)).count() > 0:
            return False
        pdp_add = self.page.locator("#add-to-cart-button").or_(
            self.page.get_by_role("button", name=re.compile(r"Add to cart", re.I))
        )
        if pdp_add.count() > 0:
            self._click_when_ready(pdp_add.first)
            self._settle_after_add()
            return True
        see_offers = self.page.get_by_role(
            "link", name=re.compile(r"See all buying options|See options", re.I)
        )
        if see_offers.count() == 0:
            return False
        self._click_when_ready(see_offers.first)
        self.wait_for_page_load()
        offer_add = self.page.get_by_role("button", name=re.compile(r"Add to cart", re.I))
        expect(offer_add.first).to_be_visible()
        expect(offer_add.first).to_be_enabled()
        offer_add.first.click()
        self._settle_after_add()
        return True

    def _add_control(self, scope):
        # Button role covers most cards. WebKit sometimes only exposes the form submit.
        return scope.get_by_role("button", name=re.compile(r"Add to cart", re.I)).or_(
            scope.locator(
                "form[action*='add-to-cart'] input[type='submit'], "
                "form[action*='add-to-cart'] button, "
                "input[name*='addToCart'], button[name*='addToCart']"
            )
        )

    def _header_cart_count(self) -> int:
        badge = self.page.locator("#nav-cart-count")
        if badge.count() == 0:
            return 0
        text = " ".join((badge.first.text_content() or "").split())
        return int(text) if text.isdigit() else 0

    def _click_when_ready(self, control) -> None:
        control.scroll_into_view_if_needed()
        expect(control).to_be_visible()
        expect(control).to_be_enabled()
        control.click()

    def _settle_after_add(self) -> None:
        # The click may ajax-update the badge or land on a bot checkpoint.
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        try:
            expect(self.page.locator("#nav-cart-count")).not_to_have_text(
                re.compile(r"^0$"), timeout=5000
            )
        except AssertionError:
            pass

    def add_first_result_to_cart(self) -> None:
        # Step 1: Results are on screen. A bot checkpoint skips the test.
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        expect(self.results.first).to_be_visible()
        for attempt in range(2):
            if self._header_cart_count() > 0:
                return
            search_url = self.page.url if re.search(r"[?&]k=", self.page.url) else ""
            clicked = self._click_first_add_control()
            if not clicked:
                raise AssertionError("No in-stock lowest-price seat cover could be added to cart")
            self._settle_after_add()
            if self._header_cart_count() > 0:
                return
            # The add click can leave the results page. Go back and try once more.
            if attempt == 0 and search_url and not re.search(r"[?&]k=", self.page.url):
                self.page.goto(search_url, wait_until="domcontentloaded")
                self.wait_for_page_load()
                self.dismiss_continue_shopping()
                expect(self.results.first).to_be_visible()

    def _click_first_add_control(self) -> bool:
        # Walk results until one can be added
        expect(self.results.first).to_be_visible()
        for i in range(min(self.results.count(), 16)):
            card = self.results.nth(i)
            if self._skip_card(card):
                continue
            add_on_card = self._add_control(card)
            # Prefer Add to cart on the card itself, once it is visible and enabled
            if add_on_card.count() > 0:
                self._click_when_ready(add_on_card.first)
                return True
            # Otherwise open the product page
            title = card.locator("h2 a").or_(card.locator("a[href*='/dp/']"))
            if title.count() == 0:
                continue
            self._click_when_ready(title.first)
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
            if self._add_from_product_page():
                return True
            self.page.go_back(wait_until="domcontentloaded")
            self.wait_for_page_load()
            expect(self.results.first).to_be_visible()
        return False
