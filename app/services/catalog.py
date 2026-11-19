"""Catalog service: chips, flavors, staff picks, search and store settings.

Stubs: each story fills in its function. The signatures are the contract
(docs/architecture/service-contracts.md); don't change them without a small
separate PR. Catalog reads should be cached for 60 seconds with
st.cache_data, and the cache cleared after an admin edit (NFR-PERF-03).
"""

from __future__ import annotations

from app.models.catalog import (
    BaseChip,
    Flavor,
    SearchFilters,
    SearchResults,
    StaffPick,
    StoreSettings,
)


def list_base_chips(*, include_inactive: bool = False) -> list[BaseChip]:
    """All base chips, featured first. Hidden chips only when include_inactive (staff).

    Stories: US-102 (U1-01), US-701 (U3-03).
    """
    raise NotImplementedError("US-102: list_base_chips")


def get_base_chip(chip_id: str) -> BaseChip | None:
    """One active base chip, or None if the id is wrong or the chip is hidden.

    Story: US-201 (U2-01).
    """
    raise NotImplementedError("US-201: get_base_chip")


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
