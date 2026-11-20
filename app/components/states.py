"""S16 system states: coming soon, empty, error, not found, not authorized, offline, footer.

Every state says what happened in plain words and offers a next step
(doc 02 section 7, S16). Wording follows the tone in doc 02 section 9.
"""

from __future__ import annotations

import streamlit as st

from app.utils import pages


def coming_soon(story_ids: str) -> None:
    """Placeholder for a screen that a story hasn't built yet."""
    st.info(f"Coming soon - {story_ids}", icon=":material/construction:")


def empty_state(
    message: str,
    *,
    action_label: str | None = None,
    action_page: str | None = None,
    icon: str = ":material/shopping_bag:",
) -> None:
    """Nothing to show yet: a friendly message and, if given, a next-step link."""
    with st.container(border=True, horizontal_alignment="center"):
        st.markdown(f"### {icon}")
        st.markdown(message)
        if action_label and action_page:
            st.page_link(action_page, label=action_label, icon=":material/arrow_forward:")


def error_state(
    message: str = "Something went wrong on our side. Nothing was charged.",
    *,
    key: str = "error_retry",
) -> bool:
    """Plain-words error with a "Try again" button. Returns True when it's clicked."""
    st.error(message, icon=":material/error:")
    return st.button("Try again", icon=":material/refresh:", key=key)


def not_found(what: str = "page") -> None:
    """404: friendly wording and a link home (doc 02 S16)."""
    st.warning(f"We couldn't find that {what}.", icon=":material/sentiment_dissatisfied:")
    st.page_link(pages.HOME, label="Back to the home page", icon=":material/home:")


def access_denied(message: str = "This page is for store staff.") -> None:
    """Not authorized, with a sign-in link. Pages normally get this via auth.require_role."""
    st.error(message, icon=":material/block:")
    st.page_link(pages.SIGN_IN, label="Sign in", icon=":material/login:")


def offline(*, key: str = "offline_retry") -> None:
    """Database unreachable (NFR-REL-01), with a "Try again" button (NFR-REL-02, doc 02 S16).

    Pressing the button simply runs the page again. Pass a different `key` if a
    page could show this twice at once.
    """
    st.warning(
        "The store is taking a snack break. Please try again in a minute.",
        icon=":material/cloud_off:",
    )
    st.button("Try again", icon=":material/refresh:", key=key)


def demo_footer() -> None:
    """Shown on every screen (NFR-PRIV-03)."""
    st.divider()
    st.caption(":material/info: Demo store, no payment needed. All products and people are made up.")
