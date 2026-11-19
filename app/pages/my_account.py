"""S10 My account. Stories: US-504, US-505, US-603. Owner: Lead (L-06).

One page, three tabs. Each tab is a component owned by a different person
(work plan section 3), so the three stories never edit this file.
"""

import streamlit as st

from app.components.flavor_passport import flavor_passport
from app.components.order_history import order_history
from app.components.profile_form import profile_form
from app.services import auth

# Any signed-in user (NFR-SEC-06).
user = auth.require_role()

st.title("My account")
orders_tab, profile_tab, passport_tab = st.tabs(["Orders", "Profile", "Flavor passport"])
with orders_tab:
    order_history(user)
with profile_tab:
    profile_form(user)
with passport_tab:
    flavor_passport(user)
