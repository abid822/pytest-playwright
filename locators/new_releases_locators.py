class NewReleasesLocators:
    URL = "https://www.amazon.com/gp/new-releases/"
    BANNER = "#zg_banner_text"  # "Amazon Hot New Releases"
    DEPARTMENT_COLUMN = "#zg-left-col"  # department list on the landing page
    RANKED_ITEM = "#gridItemRoot"  # one ranked product on a department list
    RANK_BADGE = ".zg-bdg-text"  # "#1", "#2", ...
    PRODUCT_LINK = "a[href*='/dp/']"
