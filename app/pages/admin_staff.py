"""S15 Admin: Staff (owner only). Stories: US-705. Owner: User 3 (U3-06)."""

import streamlit as st

from app.components.states import offline
from app.services import admin, auth

# Checked on every load, before anything is shown (owner only, NFR-SEC-06).
me = auth.require_role("owner")

st.caption(":material/storefront: Store Admin")
st.title("Staff")
st.caption("Give or remove the staff role. Staff can manage chips, flavors, stock and orders.")

if "admin_staff_msg" in st.session_state:
    st.success(st.session_state.pop("admin_staff_msg"), icon=":material/check_circle:")

# US-705 AC1: find a user by email.
with st.form("find_user"):
    email = st.text_input("User's email", placeholder="name@demo.test")
    looked_up = st.form_submit_button("Find", icon=":material/search:")
if looked_up:
    st.session_state["staff_lookup"] = email

lookup = st.session_state.get("staff_lookup", "")
if not lookup:
    st.stop()

try:
    person = admin.find_user(lookup)
except admin.AdminError:
    offline()
    st.stop()

if person is None:
    st.warning("No account uses that email.", icon=":material/person_off:")
    st.stop()

with st.container(border=True):
    st.markdown(f"**{person.display_name}** · {person.email}")
    st.markdown(f"Current role: **{person.role}**")

    # US-705 AC3: the owner's own row is locked (the database checks this too).
    if person.id == me.id or person.role == "owner":
        st.info("The owner's role can't be changed here.", icon=":material/lock:")
        st.stop()

    new_role = st.radio("New role", ("customer", "staff"), index=("customer", "staff").index(person.role),
                        horizontal=True, format_func=str.title)
    sure = st.checkbox(f"Yes, make {person.display_name} {new_role}", disabled=new_role == person.role)
    if st.button("Save role", type="primary", icon=":material/save:", disabled=new_role == person.role or not sure):
        try:
            admin.set_role(person.id, new_role)
        except admin.AdminError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state["admin_staff_msg"] = f"{person.display_name} is now {new_role}."
            st.rerun()
