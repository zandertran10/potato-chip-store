"""S14 Admin: Orders. Stories: US-704. Owner: Lead (L-07)."""

import streamlit as st

from app.components.badges import order_status_badge
from app.components.states import offline
from app.models.orders import ORDER_STATUSES
from app.services import auth, orders

NEXT_STATUSES = ("placed", "packed", "shipped")  # cancelling has its own button

# Checked on every load, before anything is shown (staff and owner only, NFR-SEC-06).
auth.require_role("staff", "owner")

st.caption(":material/storefront: Store Admin")
st.title("Orders")

if "admin_orders_msg" in st.session_state:
    st.success(st.session_state.pop("admin_orders_msg"), icon=":material/check_circle:")

# US-704 AC1: filter by date and status.
left, right = st.columns(2)
status = left.selectbox("Status", ["", *ORDER_STATUSES], format_func=lambda s: s.title() if s else "All")
dates = right.date_input("Placed between", value=(), help="Leave empty for all dates.")
date_from = dates[0] if len(dates) > 0 else None
date_to = dates[1] if len(dates) > 1 else date_from

try:
    found = orders.list_all_orders(status=status or None, date_from=date_from, date_to=date_to)
except orders.OrderError:
    offline()
    st.stop()

if not found:
    st.info("No orders match these filters.", icon=":material/receipt_long:")
    st.stop()

st.dataframe(
    [{"Order": o.order_number, "Placed (UTC)": f"{o.created_at:%d %b %Y %H:%M}", "Customer": o.customer_name or "-",
      "Total": f"${o.total:.2f}", "Status": o.status.title()} for o in found],
    hide_index=True, alt="Table of orders with customer, total and status",
)

by_id = {o.id: o for o in found}
order = by_id[st.selectbox("Open an order", list(by_id), format_func=lambda oid: by_id[oid].order_number)]

# US-704 AC2: customer name, email, address and lines.
with st.container(border=True):
    head, badge = st.columns([4, 1], vertical_alignment="center")
    head.markdown(f"**{order.order_number}** · ${order.total:.2f}")
    with badge:
        order_status_badge(order.status)
    st.markdown(f"**Customer:** {order.customer_name or '-'} ({order.customer_email or 'no email'})")
    st.markdown(f"**Deliver to:** {order.delivery_name}, {order.delivery_address}")
    for line in order.lines:
        st.markdown(f"- {line.quantity} × {line.base_name} + {', '.join(line.flavor_names)} · ${line.line_total:.2f}")

if order.status == "cancelled":
    st.caption("This order is cancelled. Its stock was put back.")
    st.stop()

# US-704 AC3: Placed -> Packed -> Shipped.
new_status = st.segmented_control("Status", NEXT_STATUSES, default=order.status, format_func=str.title,
                                  key=f"status_{order.id}")
if st.button("Save status", icon=":material/save:", disabled=not new_status or new_status == order.status):
    try:
        orders.set_status(order.id, new_status)
    except orders.OrderError as error:
        st.error(str(error), icon=":material/error:")
    else:
        st.session_state["admin_orders_msg"] = f"{order.order_number} is now {new_status}."
        st.rerun()

# US-704 AC4: cancel with a confirmation step; the stock goes back.
if order.status != "shipped":
    st.divider()
    sure = st.checkbox(f"Yes, cancel {order.order_number} and put its stock back", key=f"cancel_{order.id}")
    if st.button("Cancel order", icon=":material/block:", disabled=not sure):
        try:
            orders.cancel_order(order.id)
        except orders.OrderError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state["admin_orders_msg"] = f"{order.order_number} is cancelled and its stock is back."
            st.rerun()
