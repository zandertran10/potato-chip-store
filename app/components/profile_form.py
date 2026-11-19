"""My account > Profile tab (S10). Owned by User 3 (U3-08, US-505)."""

from __future__ import annotations

import streamlit as st

from app.services import profile
from app.services.auth import CurrentUser


def profile_form(user: CurrentUser) -> None:
    """Edit display name and default address; checkout fills in the saved address (US-505)."""
    try:
        saved_address = profile.get_default_address() or ""
    except profile.ProfileError as error:
        st.error(str(error), icon=":material/cloud_off:")
        return

    with st.form("profile_form"):
        name = st.text_input("Display name", value=user.display_name, max_chars=profile.MAX_NAME)
        address = st.text_area("Default delivery address", value=saved_address, max_chars=profile.MAX_ADDRESS,
                               help="Checkout fills this in for you.")
        saved = st.form_submit_button("Save", type="primary", icon=":material/save:")

    if saved:
        try:
            profile.update_profile(name, address)
        except profile.ProfileError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.success("Saved.", icon=":material/check_circle:")
