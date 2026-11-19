"""Sign-in, sign-out, register, and "who is signed in?" for every page.

Passwords are handled only by Supabase Auth; this app never stores them
(NFR-AUTH-01). Error messages stay general on purpose: a sign-in error never
says whether the email or the password was wrong (NFR-AUTH-03). Logs never
contain emails, passwords or tokens (NFR-LOG-03).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx
import streamlit as st
from postgrest.exceptions import APIError
from supabase_auth.errors import AuthApiError, AuthError

from app.services.supabase_client import forget_client, get_client
from app.utils import pages
from app.utils.session import on_sign_in

logger = logging.getLogger(__name__)

SIGN_IN_ERROR = "Email or password is wrong."
CONNECTION_ERROR = "We couldn't reach the store. Please try again in a minute."
ROLES = ("customer", "staff", "owner")

_USER_KEY = "current_user"


class AuthFailed(Exception):
    """Something the user can fix. str(error) is safe to show on screen."""


@dataclass(frozen=True)
class CurrentUser:
    """The signed-in person, as stored in st.session_state."""

    id: str
    email: str
    display_name: str
    role: str  # "customer", "staff" or "owner"


PASSWORD_RULES = ("At least 8 characters", "At least one letter", "At least one number")


def password_problems(password: str) -> list[str]:
    """Return the password rules that `password` breaks (NFR-AUTH-02).

    An empty list means the password is fine. The register page shows
    PASSWORD_RULES as a checklist that ticks off while the user types.
    """
    problems = []
    if len(password) < 8:
        problems.append(PASSWORD_RULES[0])
    if not re.search(r"[A-Za-z]", password):
        problems.append(PASSWORD_RULES[1])
    if not re.search(r"[0-9]", password):
        problems.append(PASSWORD_RULES[2])
    return problems


def _load_profile(user_id: str, email: str) -> CurrentUser:
    """Read the user's name and role from `profiles` (the database decides the role)."""
    response = (
        get_client()
        .table("profiles")
        .select("display_name, role")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    row = response.data if response else None
    if not row:
        # The sign-up trigger should always make a profile. If it didn't, use the
        # safest role rather than failing.
        return CurrentUser(id=user_id, email=email, display_name=email.split("@")[0], role="customer")
    return CurrentUser(id=user_id, email=email, display_name=row["display_name"], role=row["role"])


def sign_in(email: str, password: str) -> CurrentUser:
    """Sign in with email and password. Raises AuthFailed with a safe message."""
    email = email.strip().lower()
    if not email or not password:
        raise AuthFailed(SIGN_IN_ERROR)

    try:
        response = get_client().auth.sign_in_with_password({"email": email, "password": password})
        user = _load_profile(response.user.id, email)
    except AuthError:
        logger.warning("Sign-in failed")  # no email in the log (NFR-LOG-03)
        raise AuthFailed(SIGN_IN_ERROR) from None
    except (APIError, httpx.HTTPError) as error:
        logger.error("Sign-in could not reach Supabase: %s", type(error).__name__)
        raise AuthFailed(CONNECTION_ERROR) from None

    st.session_state[_USER_KEY] = user
    logger.info("Sign-in succeeded")
    on_sign_in()
    return user


def register(display_name: str, email: str, password: str) -> CurrentUser | None:
    """Create an account. New accounts are always customers (US-501 AC4).

    Returns the signed-in user, or None when Supabase wants the email confirmed
    first (email confirmation is on in production, NFR-AUTH-07).
    """
    display_name = display_name.strip()
    email = email.strip().lower()
    if not 1 <= len(display_name) <= 50:
        raise AuthFailed("Please enter a display name (up to 50 characters).")
    if "@" not in email:
        raise AuthFailed("Please enter a valid email address.")
    problems = password_problems(password)
    if problems:
        raise AuthFailed("Your password needs: " + ", ".join(problems).lower() + ".")

    try:
        response = get_client().auth.sign_up(
            {
                "email": email,
                "password": password,
                # Read by the database trigger that creates the profile.
                "options": {"data": {"display_name": display_name}},
            }
        )
    except AuthApiError as error:
        logger.warning("Register failed: %s", error.code)
        if error.code in ("user_already_exists", "email_exists"):
            raise AuthFailed("An account with this email already exists. Try signing in.") from None
        if error.code == "weak_password":
            raise AuthFailed("Please choose a stronger password.") from None
        raise AuthFailed("We couldn't create your account. Please try again.") from None
    except (AuthError, httpx.HTTPError) as error:
        # AuthError here = a retryable/network auth problem, not a wrong input.
        logger.error("Register could not reach Supabase: %s", type(error).__name__)
        raise AuthFailed(CONNECTION_ERROR) from None

    if response.session is None:
        logger.info("Register succeeded, waiting for email confirmation")
        return None

    user = _load_profile(response.user.id, email)
    st.session_state[_USER_KEY] = user
    logger.info("Register succeeded")
    on_sign_in()
    return user


def reset_password(email: str) -> None:
    """Start Supabase's password reset email. Always looks successful (NFR-AUTH-08).

    The page shows the same message whether or not the email exists, so nobody
    can use it to find out who has an account. Story: US-503 (U3-07).
    """
    email = email.strip().lower()
    if "@" not in email:
        return  # nothing to send; the page still shows the same message
    try:
        get_client().auth.reset_password_for_email(email)
    except (AuthError, httpx.HTTPError) as error:
        # Never tell the visitor; that would reveal whether the email exists.
        logger.warning("Password reset request failed: %s", type(error).__name__)
        return
    logger.info("Password reset requested")  # no email in the log (NFR-LOG-03)


def sign_out() -> None:
    """Sign out and clear everything this browser session was holding (US-502 AC4)."""
    try:
        get_client().auth.sign_out()
    except (AuthError, httpx.HTTPError) as error:
        # Even if Supabase can't be reached, the local session is still cleared below.
        logger.warning("Sign-out call failed: %s", type(error).__name__)
    forget_client()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    logger.info("Signed out")


def current_user() -> CurrentUser | None:
    """The signed-in user, or None for a guest."""
    return st.session_state.get(_USER_KEY)


def refresh_current_user() -> CurrentUser | None:
    """The signed-in user with their name and role read fresh from the database.

    Used by the menu, so a role given or taken away by the owner shows up on
    the next click, not only after signing in again. If the database can't be
    reached, the saved user is kept (pages still check for themselves).
    """
    user = current_user()
    if user is None:
        return None
    try:
        fresh = _load_profile(user.id, user.email)
    except (APIError, httpx.HTTPError):
        return user
    st.session_state[_USER_KEY] = fresh
    return fresh


def _sign_in_link() -> None:
    """A Sign in link that brings the visitor back to this page afterwards (US-502 AC3)."""
    here = pages.current_url_path()
    params = {"next": here} if pages.page_for(here) else None
    st.page_link(pages.SIGN_IN, label="Sign in", icon=":material/login:", query_params=params)


def require_role(*allowed_roles: str) -> CurrentUser:
    """Stop the page unless the right person is signed in. Use at the top of a page.

    require_role()                  -> any signed-in user
    require_role("staff", "owner")  -> staff and owner only

    The role is read again from the database on every page load, so a role
    change counts right away (NFR-SEC-06). Hiding a menu link is not enough;
    this check (and the database's own RLS rules) is what actually protects a page.
    """
    unknown = [role for role in allowed_roles if role not in ROLES]
    if unknown:
        raise ValueError(f"Unknown role(s): {unknown}")

    user = current_user()
    if user is None:
        st.info("Please sign in to see this page.", icon=":material/login:")
        _sign_in_link()
        st.stop()

    try:
        user = _load_profile(user.id, user.email)
    except APIError:
        # Usually an expired session: ask the person to sign in again. Only the
        # sign-in is dropped, so a guest cart in the session is kept (NFR-AUTH-05).
        st.session_state.pop(_USER_KEY, None)
        st.info("Your session has ended. Please sign in again.", icon=":material/login:")
        _sign_in_link()
        st.stop()
    except httpx.HTTPError as error:
        # Supabase unreachable: a friendly message instead of a crash (NFR-REL-01).
        logger.error("Role check could not reach Supabase: %s", type(error).__name__)
        st.error(CONNECTION_ERROR, icon=":material/cloud_off:")
        st.stop()
    st.session_state[_USER_KEY] = user

    if allowed_roles and user.role not in allowed_roles:
        st.error("This page is for store staff.", icon=":material/block:")
        # Saying which role the database gave helps spot a role that wasn't set.
        needed = "the store owner" if allowed_roles == ("owner",) else "staff or the owner"
        st.caption(f"You're signed in as {user.email}, whose role is **{user.role}**. This page needs {needed}.")
        st.stop()
    return user
