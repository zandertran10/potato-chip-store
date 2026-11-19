"""Example Streamlit AppTest for a page: S7 Sign in (app/pages/sign_in.py).

AppTest runs the app without a browser. We open the page, fill in the form,
press the button and check what's on screen. The fake Supabase from
tests/conftest.py stands in for the real one.

The page is opened THROUGH the app's entry point (app/streamlit_app.py), like a
real visitor. Opened on its own, its links to other pages would fail, because
only the entry point registers the pages.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

ENTRY_POINT = str(Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py")
SIGN_IN_PAGE = "pages/sign_in.py"


def _open_sign_in() -> AppTest:
    at = AppTest.from_file(ENTRY_POINT, default_timeout=30)
    at.switch_page(SIGN_IN_PAGE).run()
    return at


def _field(at: AppTest, label: str):
    return next(field for field in at.text_input if field.label == label)


def _sign_in(email: str, password: str) -> AppTest:
    at = _open_sign_in()
    _field(at, "Email").input(email)
    _field(at, "Password").input(password)
    next(button for button in at.button if button.label == "Sign in").click().run()
    return at


def test_page_shows_the_sign_in_form(fake_supabase):
    at = _open_sign_in()

    assert not at.exception
    assert at.title[0].value == "Sign in"
    assert _field(at, "Email") and _field(at, "Password")


def test_wrong_password_shows_the_general_error(fake_supabase):
    at = _sign_in("customer@demo.test", "WrongPass1")

    assert not at.exception
    assert [message.value for message in at.error] == ["Email or password is wrong."]


def test_right_password_signs_in(fake_supabase):
    at = _sign_in("customer@demo.test", fake_supabase.test_password)

    assert not at.exception
    assert "Casey Customer" in at.success[0].value
    assert at.session_state["current_user"].role == "customer"
