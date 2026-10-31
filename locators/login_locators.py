class LoginLocators:
    ACCOUNT_LIST = "#nav-link-accountList"  # Account & Lists in the header
    SIGN_IN_BUTTON = "#nav-flyout-ya-signin"  # Sign in inside the flyout
    ENTER_MOBILE_OR_EMAIL = "#ap_email_login, #ap_email, input[type='email']"
    # Amazon wraps Continue in span#continue; the clickable control is the inner input
    CONTINUE_BUTTON = "#continue input, #continue button, input#continue"
    INVALID_EMAIL_ALERT = "#invalid-email-alert, #auth-error-message-box, .a-alert-error"
