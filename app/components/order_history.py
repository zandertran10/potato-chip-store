"""My account > Orders tab (S10). Owned by the Lead (L-06, US-504)."""

from __future__ import annotations

import streamlit as st

from app.components.badges import order_status_badge
from app.components.states import empty_state, error_state
from app.services import orders
from app.services.auth import CurrentUser
from app.utils import pages


def order_history(user: CurrentUser) -> None:
    """The user's orders, newest first: number, date, total, status badge, then details.

    Loads its own data, so the My account page never changes. Story: US-504 (L-06).
    """
    try:
        my_orders = orders.list_my_orders()
    except orders.OrderError as error:
        if error_state(str(error), key="orders_retry"):
            st.rerun()
        return

    if not my_orders:
        # US-504 AC3.
        empty_state("No orders yet. Your first bag is a few clicks away.",
                    action_label="Build your bag", action_page=pages.SHOP, icon=":material/receipt_long:")
        return

    for order in my_orders:  # newest first (AC1)
        with st.container(border=True):
            header, status = st.columns([4, 1], vertical_alignment="center")
            with header:
                st.markdown(f"**{order.order_number}** · {order.created_at:%d %b %Y} · ${order.total:.2f}")
            with status:
                order_status_badge(order.status)
            # AC2: opening an order shows its lines.
            with st.expander("Details"):
                for line in order.lines:
                    st.markdown(
                        f"{line.quantity} × {line.base_name} + {', '.join(line.flavor_names)} · ${line.line_total:.2f}"
                    )
                st.caption(f"Delivered to {order.delivery_name}, {order.delivery_address}")
                st.page_link(pages.CONFIRMATION, label="Open order", icon=":material/open_in_new:",
                             query_params={"order": order.id})
