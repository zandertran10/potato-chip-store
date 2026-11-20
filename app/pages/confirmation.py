"""S6 Order confirmed. Stories: US-403, US-404. Owner: Lead (L-04, L-01)."""

import streamlit as st

from app.components.states import not_found, offline
from app.services import auth, orders
from app.utils import pages

# Signed-in users only (NFR-SEC-06).
user = auth.require_role()

order_id = st.query_params.get("order", "")
try:
    order = orders.get_order(order_id)
except orders.OrderError:
    offline()
    st.stop()

# US-403 AC4: someone else's order (or a made-up number) looks like "not found".
if order is None:
    not_found("order")
    st.stop()

# One short celebration, only right after placing it (doc 02 section 4). A still
# banner instead of moving balloons: Streamlit can't see the device's "reduce
# motion" setting, and doc 02 says all motion must respect it.
if st.session_state.pop("just_ordered", None) == order.id:
    st.success("Hooray! Your bag is on its way to the packing table.", icon=":material/celebration:")

st.title("Order confirmed")
st.markdown(f"## {order.order_number}")
st.caption(f"Placed on {order.created_at:%d %b %Y at %H:%M} (UTC)")

with st.container(border=True):
    for line in order.lines:
        st.markdown(f"{line.quantity} × {line.base_name} + {', '.join(line.flavor_names)} · ${line.line_total:.2f}")
    st.markdown(f"**Total: ${order.total:.2f}**")
    st.caption(f"Delivering to {order.delivery_name}, {order.delivery_address}")

# US-403 AC2. The email was saved to the outbox, never sent (US-404).
st.success(f"We've emailed your confirmation to {user.email}.", icon=":material/mail:")
st.caption("Demo store: no payment was taken.")

with st.container(horizontal=True):
    st.page_link(pages.MY_ACCOUNT, label="View my orders", icon=":material/receipt_long:")
    st.page_link(pages.SHOP, label="Keep shopping", icon=":material/storefront:")
