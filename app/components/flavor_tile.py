"""Flavor tile with its taste profile (S2, S3). Owned by User 2 (U2-02, US-202)."""

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


def flavor_tile(
    flavor: Flavor,
    *,
    selected: bool = False,
    disabled: bool = False,
    key: str,
    selectable: bool = True,
) -> bool:
    """One flavor as a card. Returns True when the shopper has it ticked.

    - Sold-out flavors are shown but can't be picked (BR-04).
    - `selected` is only the STARTING value; after that the checkbox remembers
      itself. To change it from code, set st.session_state[key] before drawing.
    - `selectable=False` shows the card without an "Add" box (shop flavor library).
    - `key` must be unique on the page, for example f"flavor_{flavor.id}".
    """
    sold_out = flavor.stock <= 0
    with st.container(border=True):
        st.markdown(f"**{flavor.icon or ''} {flavor.name}**  \n+${flavor.price:.2f} · {flavor.family}")
        if sold_out:
            stock_badge(0)
        # The popover opens in place, so choices in the builder are kept (US-202 AC3).
        with st.popover("Details", icon=":material/info:"):
            st.markdown(flavor.description)
            profile_bars(flavor)
            allergens = ", ".join(flavor.allergens) if flavor.allergens else "none"
            st.caption(f"Allergens: {allergens}")
        if not selectable:
            return False
        # Seed the starting value once, instead of passing value=, so code can
        # change the box later (staff picks) without a Streamlit warning.
        if key not in st.session_state:
            st.session_state[key] = selected and not sold_out
        if sold_out:
            st.session_state[key] = False
        # The ticked box is the check mark, so "selected" never relies on color alone.
        return st.checkbox("Add", disabled=disabled or sold_out, key=key)
