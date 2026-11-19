"""S6 Order confirmed. Stories: US-403, US-404. Owner: Lead (L-01, L-04)."""

import streamlit as st

from app.components.states import coming_soon
from app.services import auth

# Checked on every load, before anything is shown (any signed-in user, NFR-SEC-06).
auth.require_role()

st.title("Order confirmed")
order_value = st.query_params.get("order", "")  # this page reads ?order= from the link
coming_soon("US-403, US-404")
