class CustomerServiceLocators:
    URL = "https://www.amazon.com/gp/help/customer/display.html?nodeId=508510"
    SEARCH_INPUT = "#hubHelpSearchInput"  # help library search
    TOPICS = "ul.help-topics"  # topic list on the hub
    # Article titles for the topic that is currently selected
    ACTIVE_ARTICLES = ".article-wrapper.active .fs-match-card-title"
