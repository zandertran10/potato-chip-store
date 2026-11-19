"""Example unit tests for a service function: app/services/auth.py sign_in.

Pattern: arrange the fake Supabase, call the service, check the result.
No real database and no keys are used (see tests/conftest.py).
"""

import pytest

from app.services import auth


def test_sign_in_with_right_password_returns_user_and_role(fake_supabase):
    user = auth.sign_in("customer@demo.test", fake_supabase.test_password)

    assert user.display_name == "Casey Customer"
    assert user.role == "customer"
    assert auth.current_user() == user  # remembered in st.session_state


def test_sign_in_cleans_up_email_typing(fake_supabase):
    # Shoppers type spaces and capitals; sign-in should still work.
    user = auth.sign_in("  Customer@Demo.TEST ", fake_supabase.test_password)

    assert user.email == "customer@demo.test"


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("customer@demo.test", "WrongPass1"),  # right email, wrong password
        ("nobody@demo.test", "TestOnly123"),  # unknown email (the fake's test password)
        ("", ""),  # nothing typed
    ],
)
def test_sign_in_failure_gives_one_general_message(fake_supabase, email, password):
    # NFR-AUTH-03: never say whether the email or the password was wrong.
    with pytest.raises(auth.AuthFailed) as error:
        auth.sign_in(email, password)

    assert str(error.value) == "Email or password is wrong."
    assert auth.current_user() is None


def test_sign_out_clears_the_session(fake_supabase):
    auth.sign_in("staff@demo.test", fake_supabase.test_password)

    auth.sign_out()

    assert auth.current_user() is None
    assert fake_supabase.signed_out
