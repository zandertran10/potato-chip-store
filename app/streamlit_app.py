"""Potato Chip Co.: the app's entry point. Run with: streamlit run app/streamlit_app.py

This file only builds the menu, the header and the footer. Every screen lives in
app/pages/, so stories never need to edit this file (fast-track playbook, Prompt E).

Menu rules (doc 02 section 5):
- Guests and customers only get the shopping and account pages. Admin pages
  are NOT REGISTERED for them at all, so nothing about the store's internal
  pages is visible: not in the menu, and an admin address just opens Home.
- Staff also get the 4 staff pages; the owner also gets the 3 owner pages.
- Every admin page still checks the role itself (auth.require_role), and the
  database's RLS rules check again. Hiding pages is not the security; those are.
- Product, checkout, confirmation and reset-password never show in the menu:
  you reach them from links (product cards, the cart, the sign-in page).
"""

import sys
from pathlib import Path

# `streamlit run app/streamlit_app.py` only puts the app/ folder on Python's
# search path. Add the repo root too, so `from app.services import ...` works
# on laptops and on Streamlit Community Cloud alike.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# These imports must stay BELOW the path fix above, or `app` can't be found.
import streamlit as st

from app.components.header import render_header
from app.components.states import demo_footer
from app.services import auth
from app.utils import pages

st.set_page_config(page_title="Potato Chip Co.", page_icon=":material/bakery_dining:", layout="wide")

# Who's here decides what the MENU shows. Each page still checks for itself.
# The role is read fresh, so a role change shows up in the menu right away.
user = auth.refresh_current_user()
role = user.role if user else None
signed_in = user is not None
is_staff = role in ("staff", "owner")
is_owner = role == "owner"


def _page(path: str, title: str, icon: str, help_text: str, *, show: bool = True, default: bool = False):
    return st.Page(
        path,
        title=title,
        icon=icon,
        help=help_text,
        default=default,
        visibility="visible" if show else "hidden",
    )


menu = {
    "": [
        _page(pages.HOME, "Home", ":material/home:", "Start here: build your own bag of chips.", default=True),
        _page(pages.SHOP, "Shop", ":material/storefront:", "Every chip and flavor, with search and filters."),
        _page(pages.CART, "Cart", ":material/shopping_cart:", "The bags you've built, ready to check out."),
        # Reached from the cart's Checkout button, not the menu.
        _page(pages.PRODUCT, "Build your bag", ":material/bakery_dining:", "Pick a chip and its flavors.", show=False),
        _page(pages.CHECKOUT, "Checkout", ":material/shopping_bag:", "Delivery details and place your order.", show=False),
        _page(pages.CONFIRMATION, "Order confirmed", ":material/receipt_long:", "Your order number and items.", show=False),
    ],
    "Account": [
        _page(pages.SIGN_IN, "Sign in", ":material/login:", "Sign in to check out and see your orders.", show=not signed_in),
        _page(pages.REGISTER, "Register", ":material/person_add:", "Create an account to save your bags.", show=not signed_in),
        _page(pages.RESET_PASSWORD, "Forgot password", ":material/lock_reset:", "What to do if you forgot your password.", show=False),
        _page(pages.MY_ACCOUNT, "My account", ":material/account_circle:", "Your orders, profile and flavor passport.", show=signed_in),
    ],
}

# Store Admin exists only for staff and the owner (see the rules at the top).
admin_pages = []
if is_staff:
    admin_pages += [
        _page(pages.ADMIN_CHIPS, "Base chips", ":material/bakery_dining:", "Add, edit and hide base chips."),
        _page(pages.ADMIN_FLAVORS, "Flavors", ":material/category:", "Add, edit and hide flavors; set staff picks."),
        _page(pages.ADMIN_STOCK, "Stock", ":material/warehouse:", "Stock levels, restocking and history."),
        _page(pages.ADMIN_ORDERS, "Orders", ":material/local_shipping:", "Pack, ship or cancel orders."),
    ]
if is_owner:
    admin_pages += [
        _page(pages.ADMIN_STAFF, "Staff", ":material/group:", "Give or remove the staff role."),
        _page(pages.ADMIN_SETTINGS, "Settings", ":material/settings:", "Max flavors, low-stock level, featured chips."),
        _page(pages.ADMIN_DASHBOARD, "Dashboard", ":material/dashboard:", "Orders, bags sold and top flavors."),
    ]
if admin_pages:
    menu["Store Admin"] = admin_pages

current_page = st.navigation(menu, position="top")
render_header(user)

# Reserve the page's space first, draw the footer, THEN run the page inside the
# reserved space. Pages can stop early (auth.require_role calls st.stop()), which
# ends the whole run; this order keeps the demo footer on every screen (NFR-PRIV-03).
page_body = st.container()
demo_footer()
with page_body:
    current_page.run()
