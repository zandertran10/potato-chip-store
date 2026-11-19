"""Quantity stepper (S3, S4). Owned by User 2 (U2-04)."""

from __future__ import annotations

import streamlit as st


def qty_stepper(label: str, *, value: int, max_value: int, key: str, min_value: int = 1) -> int:
    """A whole-number input from min_value to max_value (the lowest stock, US-302 AC1).

    Use min_value=0 in the cart, where 0 removes the line (US-304 AC2).
    """
    max_value = max(max_value, min_value)
    return int(
        st.number_input(
            label,
            min_value=min_value,
            max_value=max_value,
            value=min(max(value, min_value), max_value),
            step=1,
            key=key,
            width=160,
        )
    )
