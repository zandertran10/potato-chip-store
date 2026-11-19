"""Staff pick cards (S1 home, S3 product). Owned by User 2 (U2-08)."""

from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from app.models.catalog import StaffPick
from app.utils import pages


def staff_picks_row(picks: Sequence[StaffPick]) -> None:
    """Up to 3 "Staff pick" cards; each opens the product page with its flavors filled in.

    Shows nothing when there are no picks. Story: US-601 (U2-08).
    """
    if not picks:
        return
    columns = st.columns(min(len(picks), 3))
    for column, pick in zip(columns, picks[:3], strict=False):
        with column, st.container(border=True):
            st.badge("Staff pick", icon=":material/star:", color="primary")
            st.markdown(f"**{pick.title}**")
            st.page_link(
                pages.PRODUCT,
                label="Try this combo",
                icon=":material/arrow_forward:",
                query_params={"id": pick.base_chip_id, "flavors": ",".join(pick.flavor_ids)},
            )
