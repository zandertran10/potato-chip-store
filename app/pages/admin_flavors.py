"""S12 Flavors and staff picks. Stories: US-702. Owner: User 3 (U3-04)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Flavors and staff picks")
coming_soon("US-702")
