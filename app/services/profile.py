"""Profile service: the signed-in customer's own display name and saved address.

RLS lets users read and edit only their own profile, and only these two
columns (migration 09). The signatures are the contract
(docs/architecture/service-contracts.md).
"""

from __future__ import annotations

import dataclasses
import logging

import httpx
import streamlit as st
from postgrest.exceptions import APIError

from app.services import auth
from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)

MAX_NAME = 50
MAX_ADDRESS = 300


class ProfileError(Exception):
    """A problem the page can show as is."""


def _run(query):
    try:
        return query.execute()
    except (APIError, httpx.HTTPError) as error:
        logger.error("Profile query failed: %s", type(error).__name__)
        raise ProfileError("We couldn't reach the store. Please try again in a minute.") from None


def get_default_address() -> str | None:
    """The signed-in user's saved address, for pre-filling checkout (US-505 AC2)."""
    user = auth.current_user()
    if user is None:
        return None
    response = _run(get_client().table("profiles").select("default_address").eq("id", user.id).maybe_single())
    row = response.data if response else None
    return (row or {}).get("default_address") or None


def update_profile(display_name: str, default_address: str | None) -> None:
    """Save the caller's display name and default address. Checkout pre-fills the address.

    Story: US-505 (U3-08).
    """
    user = auth.current_user()
    if user is None:
        raise ProfileError("Please sign in first.")
    display_name = display_name.strip()
    address = (default_address or "").strip() or None
    if not 1 <= len(display_name) <= MAX_NAME:
        raise ProfileError(f"Please enter a display name (up to {MAX_NAME} characters).")
    if address and len(address) > MAX_ADDRESS:
        raise ProfileError(f"The address can be up to {MAX_ADDRESS} characters.")

    _run(
        get_client()
        .table("profiles")
        .update({"display_name": display_name, "default_address": address})
        .eq("id", user.id)
    )
    # Keep the name in the header up to date.
    st.session_state["current_user"] = dataclasses.replace(user, display_name=display_name)
