"""S7 Sign in. Stories: US-502. Owner: User 3 (U3-01).

Email and password, one general error message, and back to the page you came
from afterwards (?next=, US-502 AC3).
"""

import streamlit as st

from app.services import auth
from app.utils import pages

# Where to go after signing in. Only our own pages are accepted (pages.page_for).
next_page = pages.page_for(st.query_params.get("next"))

with st.container(width=480):  # a centered, card-like column (doc 02, S7)
    st.title("Sign in")
    st.caption("Save your bags and track your orders.")

    user = auth.current_user()
    if user is not None:
        st.success(f"You're signed in as {user.display_name}.", icon=":material/check_circle:")
        if st.button("Sign out", icon=":material/logout:"):
            auth.sign_out()
            st.rerun()
        st.stop()

    # A form sends email and password together, only when the button is pressed.
    with st.form("sign_in_form"):
        email = st.text_input("Email", autocomplete="email")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign in", type="primary", width="stretch")

    if submitted:
        try:
            with st.spinner("Signing you in..."):
                auth.sign_in(email, password)
        except auth.AuthFailed as error:
            st.error(str(error), icon=":material/error:")
        else:
            if next_page:
                st.switch_page(next_page)
            st.rerun()

    st.page_link(pages.RESET_PASSWORD, label="Forgot password?", icon=":material/lock_reset:")
    st.page_link(
        pages.REGISTER,
        label="New here? Create an account",
        icon=":material/person_add:",
        query_params={"next": st.query_params["next"]} if next_page else None,
    )
