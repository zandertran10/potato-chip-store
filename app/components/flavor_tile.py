"""Flavor tile with its taste profile (S2, S3). Owned by User 2 (U2-02)."""

from __future__ import annotations

import streamlit as st

from app.components.badges import stock_badge
from app.models.catalog import Flavor


def profile_bars(flavor: Flavor) -> None:
    """Salty, tangy, sweet and heat as bars AND numbers, 0 to 3 (US-202 AC2)."""
    for label, value in (
        ("Salty", flavor.salty),
        ("Tangy", flavor.tangy),
        ("Sweet", flavor.sweet),
        ("Heat", flavor.heat),
    ):
        st.progress(value / 3, text=f"{label} {value}/3")


def flavor_tile(flavor: Flavor, *, selected: bool = False, disabled: bool = False, key: str) -> bool:
    """One flavor as a card. Returns True when the shopper has it ticked.

    Sold-out flavors are shown but can't be picked (BR-04). `key` must be unique
    on the page, for example f"flavor_{flavor.id}".
    """
    sold_out = flavor.stock <= 0
    with st.container(border=True):
        st.markdown(f"**{flavor.icon or ''} {flavor.name}**  \n+${flavor.price:.2f}")
        if sold_out:
            stock_badge(0)
        with st.popover("Details", icon=":material/info:"):
            st.markdown(flavor.description)
            profile_bars(flavor)
            allergens = ", ".join(flavor.allergens) if flavor.allergens else "none"
            st.caption(f"Allergens: {allergens}")
        return st.checkbox(
            "Add",
            value=selected and not sold_out,
            disabled=disabled or sold_out,
            key=key,
        )
