"""S11 Base chips. Stories: US-701. Owner: User 3 (U3-03)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Base chips")
coming_soon("US-701")
