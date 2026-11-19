"""S13 Stock. Stories: US-703. Owner: User 3 (U3-05)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Stock")
coming_soon("US-703")
