"""Shop filters (S2): sidebar on desktop, expander on mobile. Owned by User 1 (U1-04)."""

from __future__ import annotations

from collections.abc import Sequence

from app.components.states import coming_soon
from app.models.catalog import SearchFilters


def search_filters(*, styles: Sequence[str], families: Sequence[str]) -> SearchFilters:
    """Show style, family, heat, in-stock and price filters; return what's picked.

    Includes a "Clear filters" link. Story: US-104 (U1-04).
    """
    coming_soon("US-104")
    return SearchFilters()
