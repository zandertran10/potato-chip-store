"""The Supabase client: the one way the app talks to the database.

Pages never import this directly; they call the other services (CLAUDE.md layers).
"""

from __future__ import annotations

import streamlit as st

from app.config.settings import get_settings
from supabase import Client, create_client

_CLIENT_KEY = "supabase_client"


def get_client() -> Client:
    """Return this browser session's own Supabase client.

    Why one client per session, kept in st.session_state, and not one shared
    client cached with st.cache_resource: after sign-in, the client holds that
    person's tokens. A shared client would sign every visitor in as whoever
    signed in last. Keeping it in session state also means the tokens stay in
    st.session_state, never in links or logs (NFR-AUTH-04).
    """
    if _CLIENT_KEY not in st.session_state:
        settings = get_settings()
        st.session_state[_CLIENT_KEY] = create_client(
            settings.supabase_url, settings.supabase_anon_key
        )
    return st.session_state[_CLIENT_KEY]


def forget_client() -> None:
    """Drop this session's client, and with it any tokens it was holding."""
    st.session_state.pop(_CLIENT_KEY, None)
