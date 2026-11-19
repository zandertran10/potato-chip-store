"""S7 Sign in (US-502). Email and password, one general error message."""

import streamlit as st

from app.services import auth
from app.utils import pages

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
        st.rerun()

st.page_link(pages.RESET_PASSWORD, label="Forgot password?", icon=":material/lock_reset:")
st.page_link(pages.REGISTER, label="New here? Create an account", icon=":material/person_add:")
