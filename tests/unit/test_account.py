"""Account stories: US-501 register, US-502 sign in (return to ?next=), US-503 reset password."""

import pytest

from app.services import auth
from app.utils import pages

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


# US-503 Reset password --------------------------------------------------------------------

def test_reset_password_asks_supabase_to_send_the_email(fake_supabase):
    auth.reset_password("  Customer@Demo.test ")

    assert fake_supabase.reset_emails == ["customer@demo.test"]


def test_reset_password_never_complains(fake_supabase):
    # Unknown emails, junk and network trouble all look the same to the visitor (AC2).
    auth.reset_password("nobody@demo.test")
    auth.reset_password("junk")

    def broken(email, options=None):
        raise auth.AuthError("network", None)

    fake_supabase.auth.reset_password_for_email = broken
    auth.reset_password("customer@demo.test")  # no exception


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
