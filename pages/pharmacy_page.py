import re
from urllib.parse import urljoin

from playwright.sync_api import expect

from locators.pharmacy_locators import PharmacyLocators
from pages.base_page import BasePage

# Links that stay on the Pharmacy home page. Promo tiles rotate.
# RxPass is the savings card, not the hidden menu label.
CORE_LINKS = [
    ("How it works", "how_it_works"),
    ("PillPack", "pillpack"),
    ("Learn more about RxPass", "rxpass"),
]


class PharmacyPage(BasePage):
    """Amazon Pharmacy: store sections, then the RxPass monthly price."""

    def _selector(self, key: str) -> str:
        return {
            "how_it_works": PharmacyLocators.HOW_IT_WORKS_LINK,
            "pillpack": PharmacyLocators.PILLPACK_LINK,
            "rxpass": PharmacyLocators.RXPASS_LINK,
        }[key]

    def _link(self, key: str, name: str):
        # Link text includes surrounding whitespace. Prefer a visible match.
        # Amazon keeps a hidden copy of some of the same labels.
        pattern = re.compile(re.escape(name), re.I)
        if key != "rxpass":
            pattern = re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
        matches = self.page.locator(self._selector(key)).filter(has_text=pattern)
        for index in range(matches.count()):
            item = matches.nth(index)
            try:
                if item.is_visible():
                    return item
            except Exception:
                continue
        return matches.first

    def _medication_heading(self):
        return self.page.get_by_role(
            "heading", name=re.compile(r"^See if we have your medication$", re.I)
        )

    def _pharmacy_ready(self) -> bool:
        # The document title says Pharmacy, and the medication finder has painted.
        try:
            title = self.page.title() or ""
            if not re.search(r"Pharmacy", title, re.I):
                return False
            heading = self._medication_heading()
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_pharmacy(self) -> None:
        # Step 1: Open Amazon Pharmacy.
        # The first response is sometimes a shell with no finder.
        self.open(PharmacyLocators.URL)
        for _ in range(2):
            if self._pharmacy_ready():
                break
            # A reload paints the store. A second goto of the same URL does not.
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        # Step 2: The Pharmacy home page is showing, not a bot checkpoint.
        # The document title says "Amazon Pharmacy".
        expect(self.page).to_have_url(re.compile(r"pharmacy\.amazon\.com/?(?:\?|$)", re.I))
        self.expect_title(re.compile(r"Amazon Pharmacy", re.I))
        expect(self._medication_heading().first).to_be_visible()

    def expect_core_sections(self, names: list[tuple[str, str]] | None = None) -> None:
        # Step 1: The medication finder is on screen
        expect(self._medication_heading().first).to_be_visible()
        expect(self.page.locator(PharmacyLocators.MED_SEARCH_LABEL).first).to_be_visible()
        expect(self.page.locator(PharmacyLocators.MED_SEARCH).first).to_be_attached()
        # Step 2: How it works, PillPack, and RxPass are listed
        missing = []
        for name, key in names or CORE_LINKS:
            link = self._link(key, name)
            try:
                found = link.count() > 0 and link.is_visible()
            except Exception:
                found = False
            if not found:
                missing.append(name)
        assert not missing, f"Missing Pharmacy sections: {missing}"

    def _rxpass_heading(self):
        return self.page.get_by_role("heading", name=re.compile(r"\$\s*\d"))

    def _rxpass_ready(self) -> bool:
        try:
            title = self.page.title() or ""
            if not re.search(r"RxPass", title, re.I):
                return False
            heading = self._rxpass_heading()
            return heading.count() > 0 and heading.first.is_visible()
        except Exception:
            return False

    def open_rxpass(self) -> None:
        # Step 1: Open RxPass from the Pharmacy home page
        link = self._link("rxpass", "Learn more about RxPass")
        expect(link).to_be_visible()
        href = link.get_attribute("href") or ""
        assert href, "RxPass link has no href"
        absolute = urljoin(self.page.url, href)
        link.click()
        # Step 2: If the click does not leave the home page, follow the href
        self.expect_url_or_follow(
            re.compile(r"pharmacy\.amazon\.com/rxpass(?:\?|$)", re.I),
            absolute,
        )
        # The click sometimes lands on a shell: right URL, empty title.
        # A reload paints RxPass. A second goto of the same href does not.
        if not self._rxpass_ready():
            self.page.reload(wait_until="domcontentloaded")
            self.wait_for_page_load()
            self.dismiss_continue_shopping()
        expect(self.page).to_have_url(
            re.compile(r"pharmacy\.amazon\.com/rxpass(?:\?|$)", re.I)
        )
        self.expect_title(re.compile(r"RxPass", re.I))

    def expect_monthly_price(self) -> None:
        # RxPass shows a monthly dollar price in the hero heading.
        heading = self._rxpass_heading().first
        expect(heading).to_be_visible()
        text = " ".join((heading.text_content() or "").split())
        assert re.search(r"\$\s*\d", text), f"RxPass has no monthly price: {text!r}"
