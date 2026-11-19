"""My account > Flavor passport tab (S10). Owned by User 2 (U2-09, US-603).

Ethics (doc 02 section 4): badges are only rewards for exploring. No timers,
no streaks, no "don't lose your progress", and nothing that pushes buying.
"""

from __future__ import annotations

import streamlit as st

from app.services import catalog, orders
from app.services.auth import CurrentUser

# (flavors tried, badge name) - US-603 AC3.
BADGES = ((3, "Taster"), (6, "Explorer"), (None, "Flavor Master"))  # None = every flavor
STAMP_COLUMNS = 5


def earned_badges(tried: int, total: int) -> list[str]:
    """Badge names earned for `tried` of `total` flavors."""
    return [name for needed, name in BADGES if tried >= (total if needed is None else needed) and total > 0]


def flavor_passport(user: CurrentUser) -> None:
    """A stamp per flavor (filled = tried), "7 of 10 flavors tried", and 3 badges."""
    try:
        flavors = catalog.list_flavors()
        tried_ids = orders.flavors_tried()
    except (catalog.CatalogUnavailable, orders.OrderError):
        st.warning("The store is taking a snack break. Please try again in a minute.", icon=":material/cloud_off:")
        return

    tried = sum(1 for flavor in flavors if flavor.id in tried_ids)
    st.markdown(f"**{tried} of {len(flavors)} flavors tried**")  # AC2

    badges = earned_badges(tried, len(flavors))
    if badges:
        st.markdown(" ".join(f":orange-badge[:material/workspace_premium: {name}]" for name in badges))
    else:
        st.caption("Badges: Taster (3 flavors), Explorer (6), Flavor Master (all of them).")

    # AC1: every flavor as a stamp. Tried stamps have a check icon AND the word "Tried".
    for start in range(0, len(flavors), STAMP_COLUMNS):
        row = flavors[start : start + STAMP_COLUMNS]
        for column, flavor in zip(st.columns(STAMP_COLUMNS), row, strict=False):
            with column, st.container(border=True, horizontal_alignment="center"):
                done = flavor.id in tried_ids
                st.markdown("### :material/verified:" if done else "### :material/radio_button_unchecked:")
                st.markdown(f"**{flavor.name}**")
                st.caption("Tried" if done else "Not yet")
