"""Live bag price: base + flavors = total (S3). Owned by User 2 (U2-03)."""

from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from app.models.catalog import BaseChip, Flavor
from app.utils.pricing import bag_price


def price_summary(base: BaseChip, flavors: Sequence[Flavor], quantity: int) -> None:
    """Show each part of the price and the total for `quantity` bags (US-301 AC5)."""
    with st.container(border=True):
        st.markdown(f"{base.name}: ${base.price:.2f}")
        for flavor in flavors:
            st.markdown(f"+ {flavor.name}: ${flavor.price:.2f}")
        total = bag_price(base, flavors) * quantity
        st.markdown(f"**Total for {quantity} bag{'s' if quantity != 1 else ''}: ${total:.2f}**")
