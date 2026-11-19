"""S5 Checkout. Stories: US-401, US-402. Owner: Lead (L-02, L-03)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (any signed-in user, NFR-SEC-06).
auth.require_role()

st.title("Checkout")
coming_soon("US-401, US-402")
