"""Build Your Bag panel, the hero of S3. Owned by User 2 (U2-03, U2-04, U2-05)."""

from __future__ import annotations

from collections.abc import Sequence

from app.components.states import coming_soon
from app.models.catalog import BaseChip, Flavor


def bag_builder(
    chip: BaseChip,
    flavors: Sequence[Flavor],
    *,
    max_flavors: int,
    preselected_flavor_ids: Sequence[str] = (),
) -> None:
    """Pick 1 to max_flavors flavors, see price and allergens, add to cart.

    Uses flavor_tile, price_summary, qty_stepper and app/utils/pricing.py.
    `preselected_flavor_ids` comes from ?flavors= (staff picks, Surprise me).
    Stories: US-301 (U2-03), US-302 (U2-04), US-203 (U2-05).
    """
    coming_soon("US-301, US-302, US-203")
