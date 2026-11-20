"""Catalog service: chips, flavors, staff picks, search and store settings.

The signatures are the contract (docs/architecture/service-contracts.md);
don't change them without a small separate PR. Every database problem becomes
CatalogUnavailable, which pages show as the friendly offline message.
"""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx
from postgrest.exceptions import APIError

from app.models.catalog import (
    BaseChip,
    Flavor,
    SearchFilters,
    SearchResults,
    StaffPick,
    StoreSettings,
)
from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)

IMAGE_BUCKET = "product-images"
_BASE_CHIP_COLUMNS = (
    "id, name, description, style, thickness, crunch_level, allergens, price, stock, "
    "image_path, image_alt, is_featured, is_active, created_at"
)


class CatalogUnavailable(Exception):
    """The catalog couldn't be loaded (Supabase down or unreachable).

    Pages catch this and show states.offline() (NFR-REL-01, NFR-REL-02).
    """


def _is_uuid(value: str) -> bool:
    """True if `value` looks like a database id. Anything else can't be a chip."""
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _run(query):
    """Run a Supabase query; turn connection or database errors into CatalogUnavailable."""
    try:
        return query.execute()
    except (APIError, httpx.HTTPError) as error:
        logger.error("Catalog query failed: %s", type(error).__name__)
        raise CatalogUnavailable from None


def image_url(image_path: str | None) -> str | None:
    """Public URL for a chip or flavor image, or None if it has no image.

    Models keep the storage path (what admin pages save); pages and components
    call this when they need something st.image can load. The bucket is public.
    """
    if not image_path:
        return None
    if image_path.startswith(("http://", "https://")):
        return image_path
    return get_client().storage.from_(IMAGE_BUCKET).get_public_url(image_path)


def _base_chip_from_row(row: dict[str, Any]) -> BaseChip:
    """Turn one `base_chips` row into a BaseChip. Reused by the other catalog stories."""
    return BaseChip(
        id=row["id"],
        name=row["name"],
        description=row.get("description") or "",
        style=row["style"],
        thickness=row["thickness"],
        crunch_level=int(row["crunch_level"]),
        # str() first: the database sends money as a number, and Decimal(2.5)
        # from a float can pick up tiny rounding errors. Decimal("2.5") can't.
        price=Decimal(str(row["price"])),
        stock=int(row["stock"]),
        allergens=tuple(row.get("allergens") or ()),
        image_path=row.get("image_path"),
        image_alt=row.get("image_alt"),
        is_featured=bool(row.get("is_featured")),
        is_active=bool(row.get("is_active", True)),
        created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
    )


def _flavor_from_row(row: dict[str, Any]) -> Flavor:
    """Turn one `flavors` row into a Flavor. Money becomes an exact Decimal."""
    return Flavor(
        id=row["id"],
        name=row["name"],
        description=row.get("description") or "",
        family=row["family"],
        salty=int(row["salty"]),
        tangy=int(row["tangy"]),
        sweet=int(row["sweet"]),
        heat=int(row["heat"]),
        price=Decimal(str(row["price"])),
        stock=int(row["stock"]),
        allergens=tuple(row.get("allergens") or ()),
        icon=row.get("icon"),
        is_active=bool(row.get("is_active", True)),
    )


def _chip_rows(*, include_inactive: bool = False) -> list[dict[str, Any]]:
    """Chip rows, newest first."""
    query = get_client().table("base_chips").select(_BASE_CHIP_COLUMNS)
    if not include_inactive:
        query = query.eq("is_active", True)
    return _run(query.order("created_at", desc=True)).data or []


def _flavor_rows(*, include_inactive: bool = False) -> list[dict[str, Any]]:
    """Flavor rows, by family then name."""
    query = get_client().table("flavors").select("*")
    if not include_inactive:
        query = query.eq("is_active", True)
    return _run(query.order("family").order("name")).data or []


def list_base_chips(*, include_inactive: bool = False) -> list[BaseChip]:
    """All base chips, featured first, then A-Z. Hidden chips only when include_inactive (staff).

    Stories: US-102 (U1-01), US-701 (U3-03).
    """
    chips = [_base_chip_from_row(row) for row in _chip_rows(include_inactive=include_inactive)]
    return sorted(chips, key=lambda chip: (not chip.is_featured, chip.name.lower()))


def get_base_chip(chip_id: str) -> BaseChip | None:
    """One active base chip, or None if the id is wrong or the chip is hidden.

    Raises CatalogUnavailable if Supabase can't be reached. Story: US-201 (U2-01).
    """
    # A link like ?id=abc can't match any chip. Checking here also avoids a
    # database error, because the id column only accepts real ids (uuid).
    if not _is_uuid(chip_id):
        return None

    response = _run(
        get_client()
        .table("base_chips")
        .select(_BASE_CHIP_COLUMNS)
        .eq("id", chip_id)
        # Hidden chips count as "not found", even for staff (US-201 AC4).
        # For shoppers the database's RLS rule hides them anyway.
        .eq("is_active", True)
        .maybe_single()
    )
    row = response.data if response else None
    return _base_chip_from_row(row) if row else None


def list_flavors(*, include_inactive: bool = False) -> list[Flavor]:
    """All flavors, grouped by family then name. Hidden ones only for staff.

    Stories: US-102 (U1-01), US-202 (U2-02), US-301 (U2-03), US-702 (U3-04).
    """
    return [_flavor_from_row(row) for row in _flavor_rows(include_inactive=include_inactive)]


def featured_chips() -> list[BaseChip]:
    """Up to 4 chips staff marked as featured, for the home page (US-101 AC3).

    Story: US-101 (U1-03).
    """
    return [chip for chip in list_base_chips() if chip.is_featured][:4]


def _matches_price(price: Decimal, filters: SearchFilters) -> bool:
    if filters.min_price is not None and price < filters.min_price:
        return False
    return not (filters.max_price is not None and price > filters.max_price)


def search(query: str, filters: SearchFilters | None = None, sort: str = "featured") -> SearchResults:
    """Chips and flavors matching `query` (case-insensitive, partial words).

    Looks at chip names, chip descriptions and flavor names (US-103 AC1); an
    empty query matches everything. Filters (US-104) and sort (US-105) apply on
    top. The catalog is small (about 100 items, NFR-SCALE-02), so this runs in
    Python on the full list instead of in the database.
    Stories: US-103 (U1-02), US-104 (U1-04), US-105 (U1-05).
    """
    filters = filters or SearchFilters()
    words = (query or "").strip().lower()

    chips = [_base_chip_from_row(row) for row in _chip_rows()]  # newest first
    flavors = list_flavors()

    def chip_wanted(chip: BaseChip) -> bool:
        if words and words not in chip.name.lower() and words not in chip.description.lower():
            return False
        if filters.styles and chip.style not in filters.styles:
            return False
        if filters.in_stock_only and chip.stock <= 0:
            return False
        return _matches_price(chip.price, filters)

    def flavor_wanted(flavor: Flavor) -> bool:
        if words and words not in flavor.name.lower():
            return False
        if filters.families and flavor.family not in filters.families:
            return False
        if filters.max_heat is not None and flavor.heat > filters.max_heat:
            return False
        if filters.in_stock_only and flavor.stock <= 0:
            return False
        return _matches_price(flavor.price, filters)

    chips = [chip for chip in chips if chip_wanted(chip)]
    flavors = [flavor for flavor in flavors if flavor_wanted(flavor)]

    if sort == "price_asc":
        chips.sort(key=lambda c: c.price)
        flavors.sort(key=lambda f: f.price)
    elif sort == "price_desc":
        chips.sort(key=lambda c: c.price, reverse=True)
        flavors.sort(key=lambda f: f.price, reverse=True)
    elif sort == "name":
        chips.sort(key=lambda c: c.name.lower())
        flavors.sort(key=lambda f: f.name.lower())
    elif sort == "featured":
        chips.sort(key=lambda c: (not c.is_featured, c.name.lower()))
    # "newest": keep the database order (newest first).
    return SearchResults(chips=chips, flavors=flavors)


def list_staff_picks(base_chip_id: str | None = None) -> list[StaffPick]:
    """Staff picks for one chip (product page), or for all chips (home page), by position.

    Story: US-601 (U2-08).
    """
    query = get_client().table("staff_picks").select("*")
    if base_chip_id:
        if not _is_uuid(base_chip_id):
            return []
        query = query.eq("base_chip_id", base_chip_id)
    picks = _run(query.order("position")).data or []
    if not picks:
        return []
    pick_flavors = _run(
        get_client().table("staff_pick_flavors").select("*").in_("staff_pick_id", [p["id"] for p in picks])
    ).data or []
    return [
        StaffPick(
            id=pick["id"],
            base_chip_id=pick["base_chip_id"],
            title=pick["title"],
            position=int(pick["position"]),
            flavor_ids=tuple(row["flavor_id"] for row in pick_flavors if row["staff_pick_id"] == pick["id"]),
        )
        for pick in picks
    ]


def random_combo(*, rng: random.Random | None = None) -> tuple[str, list[str]]:
    """A random in-stock base chip id and 1 to max_flavors in-stock flavor ids.

    Raises CatalogUnavailable if nothing is in stock. `rng` lets tests use a
    fixed seed. Story: US-602 (U1-07).
    """
    rng = rng or random.Random()
    chips = [chip for chip in list_base_chips() if chip.stock > 0]
    flavors = [flavor for flavor in list_flavors() if flavor.stock > 0]
    if not chips or not flavors:
        raise CatalogUnavailable("Nothing is in stock right now.")
    how_many = rng.randint(1, min(get_settings().max_flavors, len(flavors)))
    return rng.choice(chips).id, [flavor.id for flavor in rng.sample(flavors, how_many)]


def get_settings() -> StoreSettings:
    """The store settings row (max flavors, low-stock threshold, from email).

    Falls back to the defaults if the row is missing. Stories: US-301 (U2-03), US-706 (U1-06).
    """
    response = _run(get_client().table("settings").select("*").eq("id", 1).maybe_single())
    row = response.data if response else None
    if not row:
        return StoreSettings()
    return StoreSettings(
        max_flavors=int(row["max_flavors"]),
        low_stock_threshold=int(row["low_stock_threshold"]),
        from_email=row["from_email"],
    )
