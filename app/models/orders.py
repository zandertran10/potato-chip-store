"""Order data. Names and prices are the ones saved at purchase time (NFR-DI-05)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Allowed statuses, in the order staff move through them (US-704).
ORDER_STATUSES = ("placed", "packed", "shipped", "cancelled")


@dataclass(frozen=True)
class OrderLine:
    base_name: str
    base_price: Decimal
    flavor_names: tuple[str, ...]
    unit_price: Decimal
    quantity: int
    line_total: Decimal


@dataclass(frozen=True)
class Order:
    id: str
    order_number: str  # CHIP-YYYYMMDD-####
    status: str  # one of ORDER_STATUSES
    delivery_name: str
    delivery_address: str
    total: Decimal
    created_at: datetime
    lines: tuple[OrderLine, ...] = ()
    # Filled in only for staff views (US-704 AC2).
    customer_name: str | None = None
    customer_email: str | None = None


@dataclass(frozen=True)
class PlacedOrder:
    """What place_order returns (migration 10)."""

    order_id: str
    order_number: str
    total: Decimal
    already_placed: bool  # True when the same checkout key was sent again
