"""My account > Flavor passport tab (S10). Owned by User 2 (U2-09)."""

from __future__ import annotations

from app.components.states import coming_soon
from app.services.auth import CurrentUser


def flavor_passport(user: CurrentUser) -> None:
    """A stamp per flavor (filled = tried), "7 of 10 flavors tried", and 3 badges.

    Loads its own data with catalog.list_flavors() and orders.flavors_tried().
    No timers, streaks or pressure wording (US-603 AC4). Story: US-603 (U2-09).
    """
    coming_soon("US-603")
