"""Bag rules used by the bag builder, the cart and checkout (doc 00 section 3.1)."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from app.models.catalog import BaseChip, Flavor


def bag_price(base: BaseChip, flavors: Sequence[Flavor]) -> Decimal:
    """Price of one bag: base chip price + each flavor's price (BR-02)."""
    return base.price + sum((flavor.price for flavor in flavors), Decimal(0))


def check_flavor_limit(chosen: int, max_flavors: int) -> str | None:
    """Return a message if the flavor count breaks BR-01 (1 to max_flavors), else None."""
    if chosen < 1:
        return "Pick at least 1 flavor."
    if chosen > max_flavors:
        return f"{max_flavors} flavors max. Your bag can only hold so much awesome."
    return None


def combined_allergens(base: BaseChip, flavors: Sequence[Flavor]) -> list[str]:
    """All allergens in the bag, each listed once, A-Z (US-203 AC1)."""
    allergens = set(base.allergens)
    for flavor in flavors:
        allergens.update(flavor.allergens)
    return sorted(allergens)
