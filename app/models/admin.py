"""Data for the staff and owner pages (S11-S15)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class UserSummary:
    """A user as the owner sees them on the Staff page (US-705)."""

    id: str
    email: str
    display_name: str
    role: str  # customer, staff or owner


@dataclass(frozen=True)
class StockChange:
    """One row of stock history (US-703 AC4)."""

    item_type: str  # "base" or "flavor"
    item_id: str
    item_name: str
    change: int  # + restock, - sold
    reason: str
    changed_by_name: str | None
    created_at: datetime


@dataclass(frozen=True)
class DashboardStats:
    """Owner dashboard numbers (US-707)."""

    orders_today: int
    bags_this_week: int
    low_stock_items: int
    top_flavors: list[tuple[str, int]] = field(default_factory=list)  # (name, bags sold)


@dataclass(frozen=True)
class AuditEntry:
    """One line of the owner's activity log (migration 13)."""

    created_at: datetime
    actor_name: str
    actor_role: str | None
    action: str  # insert, update or delete
    table_name: str
    summary: str  # e.g. Hid flavor "Truffle Herb"
    changes: dict = field(default_factory=dict)  # {"column": {"from": ..., "to": ...}}
