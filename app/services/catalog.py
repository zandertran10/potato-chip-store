"""Catalog service: chips, flavors, staff picks, search and store settings.

Stubs: each story fills in its function. The signatures are the contract
(docs/architecture/service-contracts.md); don't change them without a small
separate PR. Catalog reads should be cached for 60 seconds with
st.cache_data, and the cache cleared after an admin edit (NFR-PERF-03).
"""

from __future__ import annotations

import logging
import uuid
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
    "image_path, image_alt, is_featured, is_active"
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
    )


def list_base_chips(*, include_inactive: bool = False) -> list[BaseChip]:
    """All base chips, featured first. Hidden chips only when include_inactive (staff).

    Stories: US-102 (U1-01), US-701 (U3-03).
    """
    raise NotImplementedError("US-102: list_base_chips")


def get_base_chip(chip_id: str) -> BaseChip | None:
    """One active base chip, or None if the id is wrong or the chip is hidden.

    Raises CatalogUnavailable if Supabase can't be reached. Story: US-201 (U2-01).
    """
    # A link like ?id=abc can't match any chip. Checking here also avoids a
    # database error, because the id column only accepts real ids (uuid).
    if not _is_uuid(chip_id):
        return None

    try:
        response = (
            get_client()
            .table("base_chips")
            .select(_BASE_CHIP_COLUMNS)
            .eq("id", chip_id)
            # Hidden chips count as "not found", even for staff (US-201 AC4).
            # For shoppers the database's RLS rule hides them anyway.
            .eq("is_active", True)
            .maybe_single()
            .execute()
        )
    except (APIError, httpx.HTTPError) as error:
        logger.error("Could not load base chip: %s", type(error).__name__)
        raise CatalogUnavailable from None

    row = response.data if response else None
    return _base_chip_from_row(row) if row else None


def list_flavors(*, include_inactive: bool = False) -> list[Flavor]:
    """All flavors, grouped by family then name. Hidden ones only for staff.

    Stories: US-102 (U1-01), US-202 (U2-02), US-301 (U2-03), US-702 (U3-04).
    """
    raise NotImplementedError("US-102: list_flavors")


def featured_chips() -> list[BaseChip]:
    """The 3-4 chips staff marked as featured, for the home page.

    Story: US-101 (U1-03).
    """
    raise NotImplementedError("US-101: featured_chips")


def search(query: str, filters: SearchFilters | None = None, sort: str = "featured") -> SearchResults:
    """Chips and flavors matching `query` (case-insensitive, partial words).

    Looks at chip names, chip descriptions and flavor names. `sort` is a key of
    app.models.catalog.SORT_OPTIONS.
    Stories: US-103 (U1-02), US-104 (U1-04), US-105 (U1-05).
    """
    raise NotImplementedError("US-103: search")


def list_staff_picks(base_chip_id: str | None = None) -> list[StaffPick]:
    """Staff picks for one chip (product page), or for all chips (home page).

    Story: US-601 (U2-08).
    """
    raise NotImplementedError("US-601: list_staff_picks")


def random_combo() -> tuple[str, list[str]]:
    """A random in-stock base chip id and 1 to max_flavors in-stock flavor ids.

    Story: US-602 (U1-07).
    """
    raise NotImplementedError("US-602: random_combo")


def get_settings() -> StoreSettings:
    """The store settings row (max flavors, low-stock threshold, from email).

    Stories: US-301 (U2-03), US-706 (U1-06).
    """
    raise NotImplementedError("US-706: get_settings")
