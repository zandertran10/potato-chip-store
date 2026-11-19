"""Build Your Bag panel, the hero of S3. Owned by User 2 (U2-03, U2-04, U2-05).

Stories: US-301 Build a bag, US-302 Add the bag to the cart, US-203 See allergens.
"""

from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from app.components.flavor_tile import flavor_tile
from app.components.price_summary import price_summary
from app.components.qty_stepper import qty_stepper
from app.models.catalog import FLAVOR_FAMILIES, BaseChip, Flavor
from app.services import cart
from app.utils import pages
from app.utils.pricing import check_flavor_limit, combined_allergens

_ADDED_KEY = "bag_just_added"
_PREFILL_KEY = "bag_prefill"
TILE_COLUMNS = 3


def _tile_key(chip: BaseChip, flavor: Flavor) -> str:
    return f"bag_{chip.id}_{flavor.id}"


def _apply_prefill(chip: BaseChip, flavors: Sequence[Flavor], wanted: Sequence[str]) -> None:
    """Tick the flavors from ?flavors= once per new link (US-301 AC6).

    Remembered, so the shopper's own changes aren't undone on the next rerun,
    but a NEW staff pick or Surprise me link fills the builder in again.
    """
    marker = (chip.id, tuple(wanted))
    if not wanted or st.session_state.get(_PREFILL_KEY) == marker:
        return
    for flavor in flavors:
        st.session_state[_tile_key(chip, flavor)] = flavor.id in wanted and flavor.stock > 0
    st.session_state[_PREFILL_KEY] = marker


def bag_builder(
    chip: BaseChip,
    flavors: Sequence[Flavor],
    *,
    max_flavors: int,
    preselected_flavor_ids: Sequence[str] = (),
    all_chips: Sequence[BaseChip] | None = None,
) -> None:
    """Pick 1 to max_flavors flavors, see price and allergens, add to cart.

    `preselected_flavor_ids` comes from ?flavors= (staff picks, Surprise me).
    `all_chips` lets the shopper switch the base chip (doc 02, S3 step 1).
    Stories: US-301 (U2-03), US-302 (U2-04), US-203 (U2-05).
    """
    if st.session_state.pop(_ADDED_KEY, False):
        st.success("Bag added! Good choice.", icon=":material/check_circle:")
        st.page_link(pages.CART, label="View cart", icon=":material/shopping_cart:")

    # 1. Base chip: already selected, can be switched.
    if all_chips:
        options = [c.id for c in all_chips]
        names = {c.id: c.name for c in all_chips}
        picked = st.selectbox("Base chip", options, index=options.index(chip.id) if chip.id in options else 0,
                              format_func=names.get, key=f"bag_base_{chip.id}")
        if picked != chip.id:
            st.switch_page(pages.PRODUCT, query_params={"id": picked})

    if chip.stock <= 0:
        st.error("Sold out. Back soon!", icon=":material/block:")
        return

    # 2-3. Flavor tiles grouped by family, and the "2 of 3" counter (US-301 AC2, AC3).
    _apply_prefill(chip, flavors, preselected_flavor_ids)
    ticked = [f for f in flavors if st.session_state.get(_tile_key(chip, f), f.id in preselected_flavor_ids)]
    at_max = len(ticked) >= max_flavors
    st.markdown(f"**{len(ticked)} of {max_flavors} flavors chosen**")
    if at_max:
        st.caption(f"{max_flavors} flavors max. Your bag can only hold so much awesome.")

    chosen: list[Flavor] = []
    for family in FLAVOR_FAMILIES:
        family_flavors = [f for f in flavors if f.family == family]
        if not family_flavors:
            continue
        st.markdown(f"**{family}**")
        for start in range(0, len(family_flavors), TILE_COLUMNS):
            row = family_flavors[start : start + TILE_COLUMNS]
            for column, flavor in zip(st.columns(TILE_COLUMNS), row, strict=False):
                with column:
                    key = _tile_key(chip, flavor)
                    is_ticked = st.session_state.get(key, flavor.id in preselected_flavor_ids)
                    # At the maximum, the other flavors are disabled (US-301 AC3).
                    if flavor_tile(flavor, selected=flavor.id in preselected_flavor_ids,
                                   disabled=at_max and not is_ticked, key=key):
                        chosen.append(flavor)

    # 4. Combined allergens, above the button (US-203).
    allergens = combined_allergens(chip, chosen)
    with st.container(border=True):
        st.markdown(":material/warning: **Allergens in this bag:** " + (", ".join(allergens) if allergens else "none listed"))

    # 5. Quantity: 1 up to the lowest stock of the parts (US-302 AC1).
    limit = max(cart.max_quantity(chip, chosen), 1)
    quantity = qty_stepper("Bags", value=1, max_value=limit, key=f"bag_qty_{chip.id}")

    # 6. Live price (US-301 AC5).
    price_summary(chip, chosen, quantity)

    # 7. Add to cart: disabled until the choices are valid (US-302 AC2).
    problem = check_flavor_limit(len(chosen), max_flavors)
    if problem and chosen:
        st.caption(problem)
    if st.button("Add to cart", type="primary", icon=":material/add_shopping_cart:",
                 disabled=problem is not None, width="stretch"):
        try:
            cart.add_bag(chip.id, [f.id for f in chosen], quantity)
        except cart.CartError as error:
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state[_ADDED_KEY] = True
            st.rerun()  # so the header's cart count goes up right away (US-302 AC3)
