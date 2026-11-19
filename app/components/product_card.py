"""Product card for a base chip (S2 shop grid, S1 featured chips). Owned by User 1 (U1-01)."""

from __future__ import annotations

import streamlit as st

from app.components.badges import stock_badge
from app.models.catalog import BaseChip
from app.services.catalog import image_url
from app.utils import pages


def product_card(chip: BaseChip, *, low_stock_threshold: int = 10) -> None:
    """Image, name, "from $X.XX", stock badge and a "Build this bag" link (US-102 AC1)."""
    with st.container(border=True):
        image = image_url(chip.image_path)  # storage path -> public URL
        if image:
            # Alt text is required for every product image (doc 02 section 8).
            st.image(image, alt=chip.image_alt or chip.name, width="stretch")
        else:
            st.markdown("### :material/bakery_dining:")
        st.subheader(chip.name)
        st.markdown(f"from **${chip.price:.2f}**")
        stock_badge(chip.stock, low_stock_threshold=low_stock_threshold)
        st.page_link(
            pages.PRODUCT,
            label="Build this bag",
            icon=":material/add_shopping_cart:",
            query_params={"id": chip.id},
            disabled=chip.stock <= 0,
        )
