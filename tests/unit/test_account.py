"""Account stories: US-501 register, US-502 sign in (return to ?next=), US-503 reset password."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.services import auth
from app.utils import pages

ENTRY_POINT = str(Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py")

# US-501 Register ---------------------------------------------------------------------------

def test_register_creates_a_signed_in_customer(fake_supabase):
    user = auth.register("Robin", "Robin@Demo.test", "Crunchy123")

    assert user.role == "customer"  # AC4: always a customer
    assert user.email == "robin@demo.test"
    assert auth.current_user() == user


def test_register_with_an_existing_email_says_so(fake_supabase):
    with pytest.raises(auth.AuthFailed, match="already exists"):
        auth.register("Casey again", "customer@demo.test", "Crunchy123")  # AC3


@pytest.mark.parametrize(
    ("name", "email", "password", "message"),
    [
        ("", "new@demo.test", "Crunchy123", "display name"),
        ("Robin", "not-an-email", "Crunchy123", "valid email"),
        ("Robin", "new@demo.test", "short1", "at least 8 characters"),
        ("Robin", "new@demo.test", "longpassword", "at least one number"),
    ],
)
def test_register_checks_its_inputs_before_calling_supabase(fake_supabase, name, email, password, message):
    with pytest.raises(auth.AuthFailed, match=message):
        auth.register(name, email, password)
    assert email not in fake_supabase.passwords


def test_register_waits_for_email_confirmation_when_it_is_on(fake_supabase):
    fake_supabase.confirm_email = True

    assert auth.register("Robin", "robin@demo.test", "Crunchy123") is None
    assert auth.current_user() is None


def test_password_checklist_rules():
    assert auth.password_problems("") == list(auth.PASSWORD_RULES)
    assert auth.password_problems("Crunchy123") == []


# US-503 Forgot password: "Ask your trainer", no email (decisions.md D1) -------------------

def _open_forgot_password_page():
    at = AppTest.from_file(ENTRY_POINT, default_timeout=30)
    at.switch_page("pages/reset_password.py").run()
    return at


def test_forgot_password_page_says_ask_your_trainer(fake_supabase):
    at = _open_forgot_password_page()

    assert not at.exception
    assert "Ask your trainer" in at.info[0].value  # AC1


def test_forgot_password_sends_no_email_and_asks_for_none(fake_supabase):
    at = _open_forgot_password_page()

    assert len(at.text_input) == 0  # no email box: the page reveals nothing about who has an account (AC2)
    assert fake_supabase.reset_emails == []  # and nothing was asked of Supabase


def test_no_reset_email_function_is_left_in_the_app():
    # Nothing in the app can send a reset email by mistake.
    assert not hasattr(auth, "reset_password")


# US-502 Return to the page you came from ---------------------------------------------------

@pytest.mark.parametrize(
    ("next_value", "expected"),
    [
        ("checkout", pages.CHECKOUT),
        ("my_account", pages.MY_ACCOUNT),
        ("sign_in", None),  # never loop back to sign-in
        ("https://evil.example", None),  # only our own pages
        ("", None),
        (None, None),
    ],
)
def test_next_page_only_accepts_our_own_pages(next_value, expected):
    assert pages.page_for(next_value) == expected


# The menu reads the role fresh (a role change shows up without signing in again) ----

def test_refresh_current_user_picks_up_a_new_role(as_customer, fake_supabase):
    next(r for r in fake_supabase.rows("profiles") if r["email"] == "customer@demo.test")["role"] = "staff"

    assert auth.refresh_current_user().role == "staff"
    assert auth.current_user().role == "staff"


def test_refresh_current_user_keeps_the_saved_user_when_offline(as_owner, fake_supabase):
    fake_supabase.offline = True

    assert auth.refresh_current_user().role == "owner"


def test_refresh_current_user_for_a_guest_is_none(fake_supabase):
    assert auth.refresh_current_user() is None
