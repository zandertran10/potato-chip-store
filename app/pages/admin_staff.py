"""S15 Staff. Stories: US-705. Owner: User 3 (U3-06)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Staff")
coming_soon("US-705")
