import json
from pathlib import Path

import pytest


def _login_cases():
    path = Path(__file__).parent.parent / "data" / "login_credentials.json"
    rows = json.loads(path.read_text())
    return [
        pytest.param(row["username"], row["password"], id=row["username"])
        for row in rows
    ]


@pytest.mark.login
@pytest.mark.smoke
def test_invalid_login(login_page):
    # Step 1: Open the sign-in form from the header
    login_page.open_sign_in()
    # Step 2: Submit a bad email (missing @)
    login_page.submit_email("invalidemailgmail.com")
    # Step 3: Error message plus helper links should show
    login_page.expect_invalid_email_error()
    login_page.expect_sign_in_helpers()


@pytest.mark.login
@pytest.mark.parametrize("username,password", _login_cases())
def test_invalid_credentials(login_page, username, password):
    """Opens sign-in and expects each fake username and password pair to be rejected. A bot checkpoint skips the case."""
    # Step 1: Open the sign-in form from the header
    login_page.open_sign_in()
    # Step 2: Submit one username and password from data/login_credentials.json
    login_page.submit_credentials(username, password)
    # Step 3: Amazon should reject the pair
    login_page.expect_login_rejected()
