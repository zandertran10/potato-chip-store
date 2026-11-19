"""Status badges. Each one has an icon and words, never color alone (doc 02 section 8)."""

from __future__ import annotations

import streamlit as st

# Order status -> (label, icon, color)
_ORDER_STATUS = {
    "placed": ("Placed", ":material/receipt_long:", "blue"),
    "packed": ("Packed", ":material/inventory_2:", "orange"),
    "shipped": ("Shipped", ":material/local_shipping:", "green"),
    "cancelled": ("Cancelled", ":material/block:", "gray"),
}


def stock_badge(stock: int, *, low_stock_threshold: int = 10) -> None:
    """In stock / Few left / Sold out. "Few left" only for REAL low stock (doc 02 section 4)."""
    if stock <= 0:
        st.badge("Sold out", icon=":material/block:", color="red")
    elif stock <= low_stock_threshold:
        st.badge(f"Few left ({stock})", icon=":material/hourglass_empty:", color="orange")
    else:
        st.badge("In stock", icon=":material/check_circle:", color="green")


def order_status_badge(status: str) -> None:
    """Placed / Packed / Shipped / Cancelled."""
    label, icon, color = _ORDER_STATUS.get(status, (status.title(), ":material/help:", "gray"))
    st.badge(label, icon=icon, color=color)


def new_badge() -> None:
    """For recently added items."""
    st.badge("New", icon=":material/new_releases:", color="primary")
