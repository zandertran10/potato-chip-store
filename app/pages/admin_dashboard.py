"""S15 Dashboard. Stories: US-707. Owner: User 1 (U1-08)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Dashboard")
coming_soon("US-707")
