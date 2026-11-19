"""Admin service: everything on the Store Admin pages (staff and owner only).

The database's RLS rules block anyone else, whatever the app does.
Stubs: each story fills in its function. The signatures are the contract
(docs/architecture/service-contracts.md).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.models.admin import DashboardStats, StockChange, UserSummary
from app.models.catalog import BaseChip, Flavor, StoreSettings


def save_base_chip(chip: BaseChip) -> BaseChip:
    """Add a chip (empty id) or update one. Hiding = saving with is_active=False.

    Story: US-701 (U3-03).
    """
    raise NotImplementedError("US-701: save_base_chip")


def save_flavor(flavor: Flavor) -> Flavor:
    """Add a flavor (empty id) or update one. Hiding = saving with is_active=False.

    Story: US-702 (U3-04).
    """
    raise NotImplementedError("US-702: save_flavor")


def save_staff_pick(base_chip_id: str, position: int, title: str, flavor_ids: Sequence[str]) -> None:
    """Set the staff pick in `position` (1-3) for a chip. Empty flavor_ids removes it.

    Story: US-702 AC3 (U3-04).
    """
    raise NotImplementedError("US-702: save_staff_pick")


def upload_image(file_name: str, data: bytes, content_type: str) -> str:
    """Upload to the product-images bucket and return its storage path.

    JPG, PNG or WebP, 2 MB or smaller (US-701 AC3). Story: US-701 (U3-03).
    """
    raise NotImplementedError("US-701: upload_image")


def set_stock(item_type: str, item_id: str, new_stock: int, reason: str) -> None:
    """Set stock for a chip ("base") or flavor ("flavor"); the change is logged.

    Needs a set_stock database function (not written yet). Story: US-703 (U3-05).
    """
    raise NotImplementedError("US-703: set_stock")


def stock_history(item_type: str | None = None, item_id: str | None = None) -> list[StockChange]:
    """Stock changes, newest first, optionally for one item.

    Story: US-703 AC4 (U3-05).
    """
    raise NotImplementedError("US-703: stock_history")


def find_user(email: str) -> UserSummary | None:
    """Find a user by email for the owner's Staff page.

    Story: US-705 (U3-06).
    """
    raise NotImplementedError("US-705: find_user")


def set_role(user_id: str, role: str) -> None:
    """Make a user customer or staff. The owner can't change their own role.

    Needs a set_role database function (not written yet). Story: US-705 (U3-06).
    """
    raise NotImplementedError("US-705: set_role")


def save_settings(settings: StoreSettings) -> None:
    """Save the store settings row.

    Story: US-706 (U1-06).
    """
    raise NotImplementedError("US-706: save_settings")


def dashboard_stats() -> DashboardStats:
    """Orders today, bags this week, low-stock items and the top 5 flavors.

    Story: US-707 (U1-08).
    """
    raise NotImplementedError("US-707: dashboard_stats")
