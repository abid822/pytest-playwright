import re

from playwright.sync_api import expect

from locators.sell_locators import SellLocators
from pages.base_page import BasePage

# Steps that stay on the Sell overview. Incentive copy above them rotates.
START_STEPS = [
    "Choose a selling plan",
    "Create an Amazon selling account",
    "Start selling",
]

SELLING_PLANS = ["Individual", "Professional"]


class SellPage(BasePage):
    """Sell on Amazon: account steps, then priced Individual and Professional plans."""

    def _sell_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^Sell with Amazon$", re.I)
        )

    def _sell_ready(self) -> bool:
        heading = self._sell_heading()
        try:
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_sell(self) -> None:
        # Step 1: Open the Sell overview.
        # The first response is sometimes a shell with no heading.
        self.open(SellLocators.URL)
        if not self._sell_ready():
            self.page.goto(SellLocators.URL, wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Sell page is showing, not a bot checkpoint
        expect(self.page).to_have_url(re.compile(r"node=12766669011"))
        expect(self.page).to_have_title(re.compile(r"Sell", re.I))
        expect(self._sell_heading().first).to_be_visible()

    def expect_start_steps(self, names: list[str] | None = None) -> None:
        # Each account step is a heading on the overview.
        missing = []
        for name in names or START_STEPS:
            heading = self.page.get_by_role(
                "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
            )
            if heading.count() == 0:
                missing.append(name)
        assert not missing, f"Missing Sell steps: {missing}"

    def open_selling_plans(self) -> None:
        # Step 1: The selling-plans link is on the overview.
        # It targets a new tab, so follow the href in this tab.
        link = self.page.locator(SellLocators.PRICING_LINK).filter(
            has_text=re.compile(r"Select a selling plan", re.I)
        ).first
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        assert href, "Selling plans link has no href"
        if href.startswith("/"):
            href = "https://www.amazon.com" + href
        self.page.goto(href, wait_until="domcontentloaded")
        self.wait_for_page_load()
        self.dismiss_continue_shopping()
        # Step 2: Pricing page lists the plans
        expect(self.page).to_have_url(re.compile(r"sell\.amazon\.com/pricing", re.I))
        expect(self.page).to_have_title(re.compile(r"sell on Amazon", re.I))
        expect(
            self.page.get_by_role(
                "heading", name=re.compile(r"^Selling plans$", re.I)
            ).first
        ).to_be_visible()

    def _plan_price_text(self, name: str) -> str:
        heading = self.page.get_by_role(
            "heading", name=re.compile(rf"^{re.escape(name)}$", re.I)
        ).first
        expect(heading).to_be_visible()
        other = "Professional" if name == "Individual" else "Individual"
        node = heading
        text = ""
        for _ in range(6):
            node = node.locator("xpath=..")
            text = " ".join((node.inner_text() or "").split())
            if not re.search(r"\$\s*\d", text):
                continue
            if other.lower() in text.lower():
                continue
            return text
        return text

    def expect_priced_plans(self, names: list[str] | None = None) -> None:
        # Each plan heading sits with its own dollar price.
        for name in names or SELLING_PLANS:
            text = self._plan_price_text(name)
            assert re.search(r"\$\s*\d", text), f"{name} plan has no price: {text!r}"
