"""Shop filters (S2). Owned by User 1 (U1-04, US-104).

Doc 02 asks for a sidebar on desktop and an expandable section on mobile.
Streamlit can't tell which device it's on, so the filters live in one
expander, which works well on both.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

import streamlit as st

from app.models.catalog import SearchFilters

_KEYS = ("filter_styles", "filter_families", "filter_heat", "filter_in_stock", "filter_price")
_PRICE_MAX = 10.0  # a bag's base chip or flavor never costs more than this in the demo


def _clear_filters() -> None:
    """Callback for "Clear filters": forget every filter choice (US-104 AC3)."""
    for key in _KEYS:
        st.session_state.pop(key, None)


def search_filters(*, styles: Sequence[str], families: Sequence[str]) -> SearchFilters:
    """Show style, family, heat, in-stock and price filters; return what's picked.

    Filters work together with the search word (US-104 AC2). Story: US-104 (U1-04).
    """
    active = any(key in st.session_state and st.session_state[key] for key in _KEYS[:2]) or (
        st.session_state.get("filter_heat", 3) != 3
        or st.session_state.get("filter_in_stock", False)
        or tuple(st.session_state.get("filter_price", (0.0, _PRICE_MAX))) != (0.0, _PRICE_MAX)
    )
    with st.expander("Filters", icon=":material/tune:", expanded=active):
        chosen_styles = st.multiselect("Chip style", list(styles), key="filter_styles")
        chosen_families = st.multiselect("Flavor family", list(families), key="filter_families")
        max_heat = st.slider("Heat, at most", min_value=0, max_value=3, value=3, key="filter_heat")
        in_stock = st.toggle("In stock only", key="filter_in_stock")
        low, high = st.slider(
            "Price ($)", min_value=0.0, max_value=_PRICE_MAX, value=(0.0, _PRICE_MAX), step=0.25,
            key="filter_price",
        )
        st.button("Clear filters", icon=":material/filter_alt_off:", on_click=_clear_filters)

    return SearchFilters(
        styles=tuple(chosen_styles),
        families=tuple(chosen_families),
        max_heat=None if max_heat == 3 else max_heat,
        in_stock_only=in_stock,
        min_price=None if low <= 0 else Decimal(str(low)),
        max_price=None if high >= _PRICE_MAX else Decimal(str(high)),
    )
