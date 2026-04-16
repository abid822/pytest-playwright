from typing import ClassVar


class AmazonTabsLocator:

    # The parent container holding all the tabs
    NAV_CONTAINER = "#nav-xshop-container"
    # We can also target all links inside that container directly
    ALL_TABS_LINKS = "#nav-xshop-container a"
    # The 'All' hamburger menu button
    HAMBURGER_MENU = "#nav-hamburger-menu"
    # The container that appears after clicking
    MENU_CONTENT = "#hmenu-content"
    # All links inside the visible menu
    MENU_ITEMS = "#hmenu-content a.hmenu-item"
    # Top Navigation Bar Locators
    AMAZON_HAUL: ClassVar[str] = "#nav-link-amazon-haul"
    MEDICAL_CARE: ClassVar[str] = "#nav-link-health"
    AMAZON_BASICS: ClassVar[str] = "#nav-link-amazon-basics"
    BEST_SELLERS: ClassVar[str] = "#nav-link-fresh"
    BOOKS: ClassVar[str] = "#nav-link-books"
    TODAYS_DEALS: ClassVar[str] = "#nav-link-deals"
    PRIME: ClassVar[str] = "#nav-link-prime"
    GIFT_CARDS: ClassVar[str] = "#nav-link-gift-cards"
    SELL: ClassVar[str] = "#nav-link-sell"
    GROCERIES: ClassVar[str] = "#nav-link-grocery"
    NEW_RELEASES: ClassVar[str] = "#nav-link-newreleases"
    REGISTRY: ClassVar[str] = "#nav-link-registry"
