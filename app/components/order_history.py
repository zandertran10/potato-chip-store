"""My account > Orders tab (S10). Owned by the Lead (L-06)."""

from __future__ import annotations

from app.components.states import coming_soon
from app.services.auth import CurrentUser


def order_history(user: CurrentUser) -> None:
    """The user's orders, newest first: number, date, total, status badge, then details.

    Loads its own data with orders.list_my_orders(), so the My account page never
    changes. Empty state with a link to the shop. Story: US-504 (L-06).
    """
    coming_soon("US-504")
