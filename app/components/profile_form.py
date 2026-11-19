"""My account > Profile tab (S10). Owned by User 3 (U3-08)."""

from __future__ import annotations

from app.components.states import coming_soon
from app.services.auth import CurrentUser


def profile_form(user: CurrentUser) -> None:
    """Edit display name and default address; saves with profile.update_profile().

    Story: US-505 (U3-08).
    """
    coming_soon("US-505")
