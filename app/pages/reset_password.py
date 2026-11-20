"""S9 Forgot your password. Stories: US-503. Owner: User 3 (U3-07).

No reset email is sent: this demo store never sends real emails (doc 00
section 7, out of scope), learners use made-up addresses, and many are minors.
The trainer helps instead (docs/architecture/decisions.md, D1).
"""

import streamlit as st

from app.utils import pages

with st.container(width=480):
    st.title("Forgot your password?")
    st.info("Ask your trainer. They can reset your account, and then you register again "
            "with the same email.", icon=":material/support_agent:")
    st.caption("This demo store never sends emails, so there's no reset link to wait for.")
    st.page_link(pages.SIGN_IN, label="Back to sign in", icon=":material/login:")
    st.page_link(pages.REGISTER, label="Create an account", icon=":material/person_add:")
