"""S3 Build your bag. Stories: US-201, US-202, US-203, US-301, US-302, US-601. Owner: User 2 (U2-01 to U2-05, U2-08)."""

import streamlit as st

from app.components.states import coming_soon

st.title("Build your bag")
id_value = st.query_params.get("id", "")  # this page reads ?id= from the link
coming_soon("US-201, US-202, US-203, US-301, US-302, US-601")
