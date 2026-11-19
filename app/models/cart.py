"""Cart data: one line = one bag design (a base chip plus its flavors) with a quantity."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.models.catalog import BaseChip, Flavor


@dataclass(frozen=True)
class CartLine:
    id: str  # cart_items.id for saved carts; a generated id for guest carts
    base_chip: BaseChip
    flavors: tuple[Flavor, ...]
    quantity: int

    @property
    def unit_price(self) -> Decimal:
        """One bag: base chip price + each flavor's price (BR-02)."""
        return self.base_chip.price + sum((f.price for f in self.flavors), Decimal(0))

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
