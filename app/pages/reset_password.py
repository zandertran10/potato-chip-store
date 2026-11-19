"""S9 Reset your password. Stories: US-503. Owner: User 3 (U3-07).

The same message is shown whether or not the email has an account, so the
page can't be used to find out who shops here (US-503 AC2, NFR-AUTH-08).
Locally, Supabase's mail viewer (Inbucket) shows the reset email (NFR-AUTH-07).
"""

import streamlit as st

from app.services import auth
from app.utils import pages

with st.container(width=480):
    st.title("Reset your password")
    st.caption("We'll email you a link to choose a new one.")

    with st.form("reset_form"):
        email = st.text_input("Email", autocomplete="email")
        sent = st.form_submit_button("Send reset link", type="primary", width="stretch")

    if sent:
        auth.reset_password(email)
        st.success("If an account exists for that email, we've sent a reset link.", icon=":material/mail:")

    st.page_link(pages.SIGN_IN, label="Back to sign in", icon=":material/login:")
