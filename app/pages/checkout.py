"""S5 Checkout. Stories: US-401, US-402, US-404. Owner: Lead (L-02, L-03, L-01)."""

import logging
import os
import uuid
from decimal import Decimal
from pathlib import Path

import streamlit as st

from app.components.states import empty_state
from app.services import auth, cart, catalog, orders, profile
from app.utils import pages
from app.utils.outbox import write_confirmation_email

logger = logging.getLogger(__name__)
_KEY = "checkout_key"  # one idempotency key per checkout attempt (US-402 AC4)

# US-401 AC1: signed-in only; guests are sent to sign in and come back here.
user = auth.require_role()

st.title("Checkout")
st.caption("Cart → **Details** → Done")
st.info("Demo store: no payment needed.", icon=":material/info:")  # US-401 AC4

try:
    lines = cart.get_cart()
except cart.CartError as error:
    st.error(str(error), icon=":material/cloud_off:")
    st.stop()

if not lines:
    empty_state("Your cart is empty, so there's nothing to check out yet.",
                action_label="Build your bag", action_page=pages.SHOP)
    st.stop()

# US-401 AC2: the order summary (read only), with a way back to the cart.
with st.container(border=True):
    st.markdown("**Your order**")
    for line in lines:
        flavors = ", ".join(f.name for f in line.flavors)
        st.markdown(f"{line.quantity} × {line.base_chip.name} + {flavors} · ${line.line_total:.2f}")
    total = sum((line.line_total for line in lines), Decimal(0))
    st.markdown(f"**Total: ${total:.2f}**")
    st.caption(f"Signed in as {user.display_name} ({user.email})")
    st.page_link(pages.CART, label="Change the cart", icon=":material/edit:")

too_many = [line for line in lines if line.quantity > cart.max_quantity(line.base_chip, line.flavors)]
if too_many:
    st.warning("Some bags in your cart have less stock now. Please update the cart first.",
               icon=":material/warning:")

try:
    saved_address = profile.get_default_address() or ""
except profile.ProfileError:
    saved_address = ""

# US-401 AC3: delivery name and address, both required.
with st.form("checkout_form"):
    name = st.text_input("Delivery name", value=user.display_name, max_chars=100)
    address = st.text_area("Delivery address", value=saved_address, max_chars=300)
    submitted = st.form_submit_button("Place order", type="primary", icon=":material/shopping_bag:",
                                      disabled=bool(too_many), width="stretch")

if submitted:
    if not name.strip() or not address.strip():
        st.error("Please enter a delivery name and address.", icon=":material/error:")
        st.stop()
    # The same key is reused if this attempt is pressed twice, so only one order is made.
    key = st.session_state.setdefault(_KEY, str(uuid.uuid4()))
    try:
        with st.spinner("Placing your order..."):
            placed = orders.place_order(name, address, key)
    except orders.OrderError as error:
        # US-402 AC2: nothing was created; say what changed.
        st.error(str(error), icon=":material/error:")
        if error.code == "OUT_OF_STOCK":
            st.page_link(pages.CART, label="Update my cart", icon=":material/shopping_cart:")
        st.stop()

    st.session_state.pop(_KEY, None)  # the next checkout gets a fresh key

    # US-404: save the confirmation email AFTER the order exists. If that fails,
    # the order still succeeded; just log it (NFR-DI-08).
    try:
        order = orders.get_order(placed.order_id)
        if order is not None:
            from_email = catalog.get_settings().from_email
            write_confirmation_email(order, user.email, from_email, Path(os.getenv("OUTBOX_DIR", "outbox")))
    except (OSError, ValueError, orders.OrderError, catalog.CatalogUnavailable) as error:
        logger.error("Could not write the confirmation email: %s", type(error).__name__)

    st.session_state["just_ordered"] = placed.order_id
    st.switch_page(pages.CONFIRMATION, query_params={"order": placed.order_id})
