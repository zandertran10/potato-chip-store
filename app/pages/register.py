"""S8 Create your account. Stories: US-501. Owner: User 3 (U3-02).

No form here on purpose: the password checklist has to tick off WHILE the
shopper types (US-501 AC2), and widgets inside a form only update on submit.
"""

import streamlit as st

from app.services import auth
from app.utils import pages

next_page = pages.page_for(st.query_params.get("next"))

with st.container(width=480):
    st.title("Create your account")
    st.caption("Save your bags and track your orders.")

    if auth.current_user() is not None:
        st.info("You're already signed in.", icon=":material/check_circle:")
        st.page_link(pages.MY_ACCOUNT, label="Go to my account", icon=":material/account_circle:")
        st.stop()

    name = st.text_input("Display name", max_chars=50)
    email = st.text_input("Email", autocomplete="email")
    password = st.text_input("Password", type="password", autocomplete="new-password")

    # US-501 AC2: the rules, ticked off as the shopper types (icon AND text, not color alone).
    problems = auth.password_problems(password)
    for rule in auth.PASSWORD_RULES:
        met = bool(password) and rule not in problems
        icon = ":material/check_circle:" if met else ":material/radio_button_unchecked:"
        st.caption(f"{icon} {rule}{' (done)' if met else ''}")

    confirm = st.text_input("Confirm password", type="password", autocomplete="new-password")
    mismatch = bool(confirm) and confirm != password
    if mismatch:
        # Shown right under the field it belongs to (doc 02, S8).
        st.error("The passwords don't match.", icon=":material/error:")

    ready = bool(name.strip() and email.strip() and password and confirm) and not problems and not mismatch
    if st.button("Create account", type="primary", icon=":material/person_add:", disabled=not ready,
                 width="stretch"):
        try:
            with st.spinner("Creating your account..."):
                user = auth.register(name, email, password)
        except auth.AuthFailed as error:
            # US-501 AC3: e.g. "An account with this email already exists."
            st.error(str(error), icon=":material/error:")
        else:
            if user is None:
                # Email confirmation is on (production): Supabase sends a link first.
                st.success("Almost done! Check your email for a link to confirm your account.",
                           icon=":material/mail:")
                st.stop()
            st.switch_page(next_page or pages.HOME)

    st.page_link(pages.SIGN_IN, label="Already have an account? Sign in", icon=":material/login:")
