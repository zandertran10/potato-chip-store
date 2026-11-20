"""The header on every screen: store name, search, cart count, account (doc 02 section 5).

Owned by User 3 (U3-01 polishes it). The shell calls render_header(); stories
never need to edit app/streamlit_app.py to change what's in here.
"""

from __future__ import annotations

import streamlit as st

from app.services import auth, cart
from app.services.auth import CurrentUser
from app.utils import pages


def _cart_label() -> str:
    """'Cart (3)', or just 'Cart' if the count can't be loaded right now."""
    try:
        count = cart.count_bags()
    except cart.CartError:
        # The header must never break a page; the cart page explains the problem.
        return "Cart"
    return f"Cart ({count})"


def _remember_search() -> None:
    """Callback: keep the search word and clear the box.

    A widget's value can only be changed in its own callback, not after it's drawn,
    so the clearing happens here and the page switch happens in render_header().
    """
    st.session_state.header_search_go = st.session_state.header_search.strip()
    st.session_state.header_search = ""


def render_header(user: CurrentUser | None, *, current_page: str = "") -> None:
    """Store name, a search box, the cart link with its count, and sign in / account.

    `current_page` is the open page's address ("shop", "" for Home), from st.navigation.
    """
    # "bottom" keeps the links in line with the search box now that it has a label above it.
    with st.container(horizontal=True, vertical_alignment="bottom", gap="medium"):
        st.page_link(pages.HOME, label="**Potato Chip Co.**", icon=":material/bakery_dining:")

        # A visible label, not just placeholder text (doc 02 section 8).
        st.text_input(
            "Search",
            placeholder="Chips and flavors",
            label_visibility="visible",
            key="header_search",
            on_change=_remember_search,
            width=280,
        )
        query = st.session_state.pop("header_search_go", "")
        if query:
            # Put the word into the Shop page's search box (key "q"). That box is
            # tied to ?q= in the address, so Streamlit refuses to set ?q= directly
            # once it exists; setting the box updates the address by itself.
            st.session_state["q"] = query
            if current_page == "shop":
                # Already on Shop: switching to it again would try to clear ?q=,
                # which the box also blocks. Just show the new results.
                st.rerun()
            st.switch_page(pages.SHOP)

        st.page_link(pages.CART, label=_cart_label(), icon=":material/shopping_cart:")

        if user is None:
            # Come back to this page after signing in (US-502 AC3).
            here = pages.current_url_path()
            st.page_link(pages.SIGN_IN, label="Sign in", icon=":material/login:",
                         query_params={"next": here} if pages.page_for(here) else None)
        else:
            st.page_link(pages.MY_ACCOUNT, label=user.display_name, icon=":material/account_circle:")
            if st.button("Sign out", icon=":material/logout:", key="header_sign_out"):
                auth.sign_out()
                st.switch_page(pages.HOME)
