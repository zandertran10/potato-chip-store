"""S2 Shop. Stories: US-102, US-103, US-104, US-105. Owner: User 1 (U1-01, U1-02, U1-04, U1-05)."""

import streamlit as st

from app.components.states import coming_soon

st.title("Shop")
q_value = st.query_params.get("q", "")  # this page reads ?q= from the link
coming_soon("US-102, US-103, US-104, US-105")
