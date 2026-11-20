"""Catalog data: base chips, flavors, staff picks, store settings and search inputs.

These match the tables in doc 00 section 6. Services return these objects, so
pages and components never handle raw database rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal

# A chip counts as "New" for this many days after it's added.
NEW_FOR_DAYS = 14

# The five flavor families (doc 01 section 4).
FLAVOR_FAMILIES = ("Salty", "Tangy", "Spicy", "Sweet", "Herby")

# Shop sort options (US-105). The first one is the default.
SORT_OPTIONS = {
    "featured": "Featured",
    "price_asc": "Price low → high",
    "price_desc": "Price high → low",
    "name": "Name A → Z",
    "newest": "Newest",
}


@dataclass(frozen=True)
class BaseChip:
    id: str
    name: str
    description: str
    style: str
    thickness: str
    crunch_level: int  # 0-3
    price: Decimal
    stock: int
    allergens: tuple[str, ...] = ()
    image_path: str | None = None
    image_alt: str | None = None
    is_featured: bool = False
    is_active: bool = True
    created_at: datetime | None = None  # when it was added; drives the "New" badge

    def is_new(self, *, now: datetime | None = None, days: int = NEW_FOR_DAYS) -> bool:
        """Added in the last `days` days (doc 02 S2 "New" badge). Honest: based on the real date."""
        if self.created_at is None:
            return False
        now = now or datetime.now(UTC)
        return now - self.created_at <= timedelta(days=days)


@dataclass(frozen=True)
class Flavor:
    id: str
    name: str
    description: str
    family: str  # one of FLAVOR_FAMILIES
    salty: int  # 0-3
    tangy: int  # 0-3
    sweet: int  # 0-3
    heat: int  # 0-3
    price: Decimal
    stock: int
    allergens: tuple[str, ...] = ()
    icon: str | None = None
    is_active: bool = True


@dataclass(frozen=True)
class StaffPick:
    id: str
    base_chip_id: str
    title: str
    position: int  # 1-3
    flavor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StoreSettings:
    max_flavors: int = 3
    low_stock_threshold: int = 10
    from_email: str = "orders@potatochipco.test"


@dataclass(frozen=True)
class SearchFilters:
    """What the shopper picked in the shop filters (US-104). Empty = no filter."""

    styles: tuple[str, ...] = ()
    families: tuple[str, ...] = ()
    max_heat: int | None = None
    in_stock_only: bool = False
    min_price: Decimal | None = None
    max_price: Decimal | None = None


@dataclass(frozen=True)
class SearchResults:
    chips: list[BaseChip] = field(default_factory=list)
    flavors: list[Flavor] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.chips) + len(self.flavors)
