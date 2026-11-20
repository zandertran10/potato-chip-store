"""S9 Forgot password. Stories: US-503. Owner: User 3 (U3-07).

No reset email is sent: this demo store never sends real emails (doc 00
section 7, out of scope), learners use made-up addresses, and many are minors.
Our support team resets the account instead; in class, that's the trainer
(docs/architecture/decisions.md, D1). Written the way a real shop would say it.
"""

import streamlit as st

from app.utils import pages

with st.container(width=480):
    st.title("Forgot your password?")
    st.markdown("No problem, it happens to everyone.")
    st.info(
        "**Contact our customer support team** and we'll reset your account for you. "
        "Once it's reset, create your account again using the same email address.",
        icon=":material/support_agent:",
    )
    st.caption(":material/lock: For your security, we never send password reset links by email.")
    st.page_link(pages.SIGN_IN, label="Back to sign in", icon=":material/login:")
    st.page_link(pages.REGISTER, label="Create an account", icon=":material/person_add:")
