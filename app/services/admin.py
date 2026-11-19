"""Admin service: everything on the Store Admin pages (staff and owner only).

Inputs are checked here first, with messages staff can act on (NFR-SEC-13).
The database's RLS rules and functions check again, whatever the app does.
The signatures are the contract (docs/architecture/service-contracts.md).
"""

from __future__ import annotations

import logging
import re
import uuid
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
from postgrest.exceptions import APIError

from app.models.admin import DashboardStats, StockChange, UserSummary
from app.models.catalog import FLAVOR_FAMILIES, BaseChip, Flavor, StoreSettings
from app.services import catalog
from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)

IMAGE_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}  # US-701 AC3
MAX_IMAGE_BYTES = 2 * 1024 * 1024
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+$")
_FRIENDLY = {
    "NOT_ALLOWED": "You don't have permission to do that.",
    "NOT_FOUND": "That item doesn't exist any more.",
}


class AdminError(Exception):
    """A problem staff can act on. str(error) is safe to show."""


def _run(query):
    try:
        return query.execute()
    except APIError as error:
        code, _, detail = (error.message or "").partition(": ")
        if error.code == "23505":  # unique_violation
            raise AdminError("That name is already used. Please pick another.") from None
        if code == "BAD_INPUT":
            raise AdminError(detail) from None
        if code in _FRIENDLY:
            raise AdminError(_FRIENDLY[code]) from None
        logger.error("Admin query failed (database error %s)", error.code)
        raise AdminError("That didn't save. Please check the fields and try again.") from None
    except httpx.HTTPError as error:
        logger.error("Admin query failed: %s", type(error).__name__)
        raise AdminError("We couldn't reach the store. Please try again in a minute.") from None


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdminError(message)


def _check_text(value: str, label: str, longest: int, *, required: bool = True) -> None:
    if required:
        _require(1 <= len(value.strip()) <= longest, f"{label} is required (up to {longest} characters).")
    else:
        _require(len(value) <= longest, f"{label} can be up to {longest} characters.")


def _check_money_and_stock(price: Decimal, stock: int) -> None:
    _require(price > 0, "Price must be above 0.")  # US-701 AC2
    _require(price == price.quantize(Decimal("0.01")), "Price can have at most 2 decimals.")
    _require(isinstance(stock, int) and stock >= 0, "Stock must be a whole number of 0 or more.")


def _check_alt_text(image_path: str | None, image_alt: str | None) -> None:
    if image_path:
        # Every product image needs alt text (doc 02 section 8).
        _require(bool((image_alt or "").strip()), "Please add alt text that describes the image.")
    _require(len(image_alt or "") <= 150, "Alt text can be up to 150 characters.")


# --- US-701 Base chips -----------------------------------------------------------------

def save_base_chip(chip: BaseChip) -> BaseChip:
    """Add a chip (empty id) or update one. Hiding = saving with is_active=False.

    Stock is only set when a chip is added; after that it changes through
    set_stock, so every change is logged (US-703). Story: US-701 (U3-03).
    """
    _check_text(chip.name, "Name", 60)
    _check_text(chip.description, "Description", 500, required=False)
    _check_text(chip.style, "Style", 30)
    _check_text(chip.thickness, "Thickness", 30)
    _require(0 <= chip.crunch_level <= 3, "Crunch level must be 0 to 3.")
    _check_money_and_stock(chip.price, chip.stock)
    _check_alt_text(chip.image_path, chip.image_alt)

    values = {
        "name": chip.name.strip(),
        "description": chip.description.strip(),
        "style": chip.style.strip(),
        "thickness": chip.thickness.strip(),
        "crunch_level": chip.crunch_level,
        "allergens": sorted({a.strip().lower() for a in chip.allergens if a.strip()}),
        "price": str(chip.price),  # a string keeps the exact amount
        "image_path": chip.image_path or None,
        "image_alt": (chip.image_alt or "").strip() or None,
        "is_featured": chip.is_featured,
        "is_active": chip.is_active,
    }
    if not chip.id:
        rows = _run(get_client().table("base_chips").insert({**values, "stock": chip.stock})).data
    else:
        rows = _run(get_client().table("base_chips").update(values).eq("id", chip.id)).data
    _require(bool(rows), "That chip couldn't be saved (it may have been removed, or you may not be staff).")
    logger.info("Base chip saved")
    return catalog._base_chip_from_row(rows[0])


# --- US-702 Flavors and staff picks ------------------------------------------------------

def save_flavor(flavor: Flavor) -> Flavor:
    """Add a flavor (empty id) or update one. Hiding = saving with is_active=False.

    Story: US-702 (U3-04).
    """
    _check_text(flavor.name, "Name", 60)
    _check_text(flavor.description, "Description", 500, required=False)
    _require(flavor.family in FLAVOR_FAMILIES, "Pick a flavor family.")
    for label, score in (("Salty", flavor.salty), ("Tangy", flavor.tangy), ("Sweet", flavor.sweet),
                         ("Heat", flavor.heat)):
        _require(0 <= score <= 3, f"{label} must be 0 to 3.")
    _check_money_and_stock(flavor.price, flavor.stock)

    values = {
        "name": flavor.name.strip(),
        "description": flavor.description.strip(),
        "family": flavor.family,
        "salty": flavor.salty,
        "tangy": flavor.tangy,
        "sweet": flavor.sweet,
        "heat": flavor.heat,
        "allergens": sorted({a.strip().lower() for a in flavor.allergens if a.strip()}),
        "price": str(flavor.price),
        "icon": (flavor.icon or "").strip() or None,
        "is_active": flavor.is_active,
    }
    if not flavor.id:
        rows = _run(get_client().table("flavors").insert({**values, "stock": flavor.stock})).data
    else:
        rows = _run(get_client().table("flavors").update(values).eq("id", flavor.id)).data
    _require(bool(rows), "That flavor couldn't be saved (it may have been removed, or you may not be staff).")
    logger.info("Flavor saved")
    return catalog._flavor_from_row(rows[0])


def save_staff_pick(base_chip_id: str, position: int, title: str, flavor_ids: Sequence[str]) -> None:
    """Set the staff pick in `position` (1-3) for a chip. Empty flavor_ids removes it.

    Story: US-702 AC3 (U3-04).
    """
    _require(position in (1, 2, 3), "A chip can have staff picks 1, 2 and 3.")
    flavor_ids = list(dict.fromkeys(flavor_ids))
    if flavor_ids:
        _check_text(title, "Title", 60)
        _require(1 <= len(flavor_ids) <= 3, "A staff pick has 1 to 3 flavors.")

    # Replace whatever is in this slot. Deleting the pick also deletes its flavors.
    _run(get_client().table("staff_picks").delete().eq("base_chip_id", base_chip_id).eq("position", position))
    if not flavor_ids:
        return
    pick = _run(get_client().table("staff_picks").insert(
        {"base_chip_id": base_chip_id, "position": position, "title": title.strip()})).data[0]
    _run(get_client().table("staff_pick_flavors").insert(
        [{"staff_pick_id": pick["id"], "flavor_id": flavor_id} for flavor_id in flavor_ids]))


def upload_image(file_name: str, data: bytes, content_type: str) -> str:
    """Upload to the product-images bucket and return its storage path.

    JPG, PNG or WebP, 2 MB or smaller (US-701 AC3, NFR-SEC-16). The file gets a
    new random name, so nothing in the original file name ends up in the path.
    Story: US-701 (U3-03).
    """
    _require(content_type in IMAGE_TYPES, "Images must be JPG, PNG or WebP.")
    _require(0 < len(data) <= MAX_IMAGE_BYTES, "Images must be 2 MB or smaller.")
    path = f"products/{uuid.uuid4().hex}.{IMAGE_TYPES[content_type]}"
    try:
        get_client().storage.from_(catalog.IMAGE_BUCKET).upload(path, data, {"content-type": content_type})
    except Exception as error:  # noqa: BLE001 - the storage client raises several error types
        logger.error("Image upload failed: %s", type(error).__name__)
        raise AdminError("The image didn't upload. Please try again.") from None
    return path


# --- US-703 Stock --------------------------------------------------------------------------

def set_stock(item_type: str, item_id: str, new_stock: int, reason: str) -> None:
    """Set stock for a chip ("base") or flavor ("flavor"); the change is logged (migration 11).

    Story: US-703 (U3-05).
    """
    _require(item_type in ("base", "flavor"), "Unknown item type.")
    _require(isinstance(new_stock, int) and new_stock >= 0, "Stock must be a whole number of 0 or more.")
    _check_text(reason, "A reason", 200)  # US-703 AC3
    _run(get_client().rpc("set_stock", {"p_item_type": item_type, "p_item_id": item_id,
                                        "p_new_stock": new_stock, "p_reason": reason.strip()}))
    logger.info("Stock changed")


def stock_history(item_type: str | None = None, item_id: str | None = None) -> list[StockChange]:
    """Stock changes, newest first (the last 200), optionally for one item. Story: US-703 AC4."""
    query = get_client().table("stock_history").select("*")
    if item_type:
        query = query.eq("item_type", item_type)
    if item_id:
        query = query.eq("item_id", item_id)
    rows = _run(query.order("created_at", desc=True).limit(200)).data or []
    if not rows:
        return []
    names = {chip.id: chip.name for chip in catalog.list_base_chips(include_inactive=True)}
    names.update({flavor.id: flavor.name for flavor in catalog.list_flavors(include_inactive=True)})
    people_ids = sorted({row["changed_by"] for row in rows if row.get("changed_by")})
    people = {}
    if people_ids:
        people = {p["id"]: p["display_name"] for p in _run(
            get_client().table("profiles").select("id, display_name").in_("id", people_ids)).data or []}
    return [
        StockChange(
            item_type=row["item_type"],
            item_id=row["item_id"],
            item_name=names.get(row["item_id"], "(removed item)"),
            change=int(row["change"]),
            reason=row["reason"],
            changed_by_name=people.get(row.get("changed_by")),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


# --- US-705 Staff --------------------------------------------------------------------------

def find_user(email: str) -> UserSummary | None:
    """Find a user by email for the owner's Staff page. Story: US-705 (U3-06)."""
    email = email.strip().lower()
    if not _EMAIL.match(email):
        return None
    response = _run(get_client().table("profiles").select("id, email, display_name, role")
                    .eq("email", email).maybe_single())
    row = response.data if response else None
    if not row:
        return None
    return UserSummary(id=row["id"], email=row["email"], display_name=row["display_name"], role=row["role"])


def set_role(user_id: str, role: str) -> None:
    """Make a user customer or staff. The owner can't change their own role (migration 11).

    Story: US-705 (U3-06).
    """
    _require(role in ("customer", "staff"), "The role must be customer or staff.")
    _run(get_client().rpc("set_role", {"p_user_id": user_id, "p_role": role}))
    logger.info("Role changed to %s", role)


# --- US-706 Settings, US-707 Dashboard -------------------------------------------------------

def save_settings(settings: StoreSettings) -> None:
    """Save the store settings row. Story: US-706 (U1-06)."""
    _require(1 <= settings.max_flavors <= 5, "Maximum flavors must be 1 to 5.")
    _require(settings.low_stock_threshold >= 0, "The low-stock level must be 0 or more.")
    _require(bool(_EMAIL.match(settings.from_email.strip())), "Please enter a valid 'from' email address.")
    rows = _run(get_client().table("settings").update({
        "max_flavors": settings.max_flavors,
        "low_stock_threshold": settings.low_stock_threshold,
        "from_email": settings.from_email.strip(),
    }).eq("id", 1)).data
    _require(bool(rows), "Only the store owner can change settings.")


def dashboard_stats(*, now: datetime | None = None) -> DashboardStats:
    """Orders today, bags this week, low-stock items and the top 5 flavors (UTC days).

    Cancelled orders don't count. `now` lets tests fix the date. Story: US-707 (U1-08).
    """
    now = now or datetime.now(UTC)
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()

    order_rows = [row for row in _run(get_client().table("orders").select("id, status, created_at")).data or []
                  if row["status"] != "cancelled"]
    item_rows = []
    if order_rows:
        item_rows = _run(get_client().table("order_items").select("id, order_id, quantity")
                         .in_("order_id", [row["id"] for row in order_rows])).data or []
    recent = {row["id"] for row in order_rows if row["created_at"] >= week_ago}

    flavor_rows = []
    if item_rows:
        flavor_rows = _run(get_client().table("order_item_flavors").select("order_item_id, flavor_name")
                           .in_("order_item_id", [row["id"] for row in item_rows])).data or []
    bags_per_item = {row["id"]: int(row["quantity"]) for row in item_rows}
    top = Counter()
    for row in flavor_rows:
        top[row["flavor_name"]] += bags_per_item.get(row["order_item_id"], 0)

    threshold = catalog.get_settings().low_stock_threshold
    low = sum(1 for item in [*catalog.list_base_chips(), *catalog.list_flavors()] if item.stock <= threshold)

    return DashboardStats(
        orders_today=sum(1 for row in order_rows if row["created_at"][:10] == today),
        bags_this_week=sum(int(row["quantity"]) for row in item_rows if row["order_id"] in recent),
        low_stock_items=low,
        top_flavors=top.most_common(5),
    )
