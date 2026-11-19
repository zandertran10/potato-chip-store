"""Cart service: works for guests (cart in st.session_state) and customers (saved cart).

- A guest's cart lives in st.session_state for this browser session (US-305 AC1).
- A signed-in customer's cart is saved in the database, so it's still there next
  visit (US-305 AC3). The database's RLS rules let customers touch only their own cart.
- One line = one bag design: a base chip plus a set of flavors, with a quantity.

The signatures are the contract (docs/architecture/service-contracts.md).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence

import httpx
import streamlit as st
from postgrest.exceptions import APIError

from app.models.cart import CartLine
from app.models.catalog import BaseChip, Flavor
from app.services import auth, catalog
from app.services.supabase_client import get_client
from app.utils.pricing import check_flavor_limit

logger = logging.getLogger(__name__)

GUEST_CART_KEY = "guest_cart"
MAX_BAGS_PER_LINE = 99  # matches the database CHECK (quantity between 1 and 99)


class CartError(Exception):
    """Something the shopper can fix, or a friendly "try again". str(error) is safe to show."""


def _run(query):
    try:
        return query.execute()
    except (APIError, httpx.HTTPError) as error:
        logger.error("Cart query failed: %s", type(error).__name__)
        raise CartError("We couldn't reach the store. Please try again in a minute.") from None


# --- Where the cart lives -----------------------------------------------------------

def _user_id() -> str | None:
    user = auth.current_user()
    return user.id if user else None


def _guest_lines() -> list[dict]:
    """The guest cart: a list of {"id", "base_chip_id", "flavor_ids", "quantity"}."""
    return st.session_state.setdefault(GUEST_CART_KEY, [])


def _cart_id(user_id: str, *, create: bool) -> str | None:
    """The customer's saved cart id; makes the cart the first time if `create`."""
    response = _run(get_client().table("carts").select("id").eq("user_id", user_id).maybe_single())
    if response and response.data:
        return response.data["id"]
    if not create:
        return None
    return _run(get_client().table("carts").insert({"user_id": user_id})).data[0]["id"]


def _saved_lines(user_id: str) -> list[dict]:
    """The customer's saved cart in the same shape as a guest cart."""
    cart_id = _cart_id(user_id, create=False)
    if not cart_id:
        return []
    items = _run(
        get_client().table("cart_items").select("id, base_chip_id, quantity").eq("cart_id", cart_id).order("created_at")
    ).data or []
    if not items:
        return []
    item_flavors = _run(
        get_client().table("cart_item_flavors").select("*").in_("cart_item_id", [item["id"] for item in items])
    ).data or []
    return [
        {
            "id": item["id"],
            "base_chip_id": item["base_chip_id"],
            "flavor_ids": sorted(row["flavor_id"] for row in item_flavors if row["cart_item_id"] == item["id"]),
            "quantity": int(item["quantity"]),
        }
        for item in items
    ]


def _raw_lines() -> list[dict]:
    user_id = _user_id()
    return _saved_lines(user_id) if user_id else list(_guest_lines())


# --- Rules ---------------------------------------------------------------------------

def max_quantity(base_chip: BaseChip, flavors: Sequence[Flavor]) -> int:
    """Most bags of one design the shop can make: the lowest stock of its parts (US-302 AC1)."""
    return min([base_chip.stock, *(flavor.stock for flavor in flavors), MAX_BAGS_PER_LINE])


def _catalog_maps() -> tuple[dict[str, BaseChip], dict[str, Flavor]]:
    try:
        chips = {chip.id: chip for chip in catalog.list_base_chips()}
        flavors = {flavor.id: flavor for flavor in catalog.list_flavors()}
    except catalog.CatalogUnavailable:
        raise CartError("We couldn't reach the store. Please try again in a minute.") from None
    return chips, flavors


def _check_design(base_chip_id: str, flavor_ids: Sequence[str]) -> tuple[BaseChip, list[Flavor]]:
    """Check one bag design against the catalog and the rules; return its parts."""
    chips, flavors = _catalog_maps()
    chip = chips.get(base_chip_id)
    if chip is None:
        raise CartError("That chip isn't available any more.")
    unique_ids = list(dict.fromkeys(flavor_ids))
    try:
        max_flavors = catalog.get_settings().max_flavors
    except catalog.CatalogUnavailable:
        raise CartError("We couldn't reach the store. Please try again in a minute.") from None
    problem = check_flavor_limit(len(unique_ids), max_flavors)  # BR-01
    if problem:
        raise CartError(problem)
    chosen = [flavors.get(fid) for fid in unique_ids]
    if any(flavor is None for flavor in chosen):
        raise CartError("One of those flavors isn't available any more.")
    sold_out = [part.name for part in (chip, *chosen) if part.stock <= 0]
    if sold_out:
        raise CartError(f"Sold out: {', '.join(sold_out)}. Back soon!")  # BR-04
    return chip, chosen


# --- Public functions ----------------------------------------------------------------

def get_cart() -> list[CartLine]:
    """Every line in the current cart (guest or signed-in customer).

    Lines whose chip or flavor is no longer sold are left out. Story: US-303 (U2-06).
    """
    raw = _raw_lines()
    if not raw:
        return []
    chips, flavors = _catalog_maps()
    lines = []
    for line in raw:
        chip = chips.get(line["base_chip_id"])
        parts = [flavors.get(fid) for fid in line["flavor_ids"]]
        if chip is None or any(part is None for part in parts):
            continue
        lines.append(
            CartLine(
                id=line["id"],
                base_chip=chip,
                flavors=tuple(sorted(parts, key=lambda f: f.name)),
                quantity=line["quantity"],
            )
        )
    return lines


def count_bags() -> int:
    """Total number of bags in the cart, for the header badge. Story: US-302 (U2-04)."""
    return sum(line["quantity"] for line in _raw_lines())


def add_bag(base_chip_id: str, flavor_ids: Sequence[str], quantity: int) -> None:
    """Add a bag. The same base and flavors again raises that line's quantity (US-302 AC4).

    Never above the lowest stock of the chip and its flavors (US-302 AC1).
    Raises CartError with a message the page can show. Story: US-302 (U2-04).
    """
    if quantity < 1:
        raise CartError("Choose at least 1 bag.")
    chip, chosen = _check_design(base_chip_id, flavor_ids)
    design = sorted(flavor.id for flavor in chosen)
    limit = max_quantity(chip, chosen)

    user_id = _user_id()
    if user_id is None:
        lines = _guest_lines()
        for line in lines:
            if line["base_chip_id"] == chip.id and line["flavor_ids"] == design:
                line["quantity"] = min(line["quantity"] + quantity, limit)
                return
        lines.append({"id": str(uuid.uuid4()), "base_chip_id": chip.id, "flavor_ids": design,
                      "quantity": min(quantity, limit)})
        return

    for line in _saved_lines(user_id):
        if line["base_chip_id"] == chip.id and line["flavor_ids"] == design:
            _run(get_client().table("cart_items")
                 .update({"quantity": min(line["quantity"] + quantity, limit)}).eq("id", line["id"]))
            return
    cart_id = _cart_id(user_id, create=True)
    item = _run(get_client().table("cart_items").insert(
        {"cart_id": cart_id, "base_chip_id": chip.id, "quantity": min(quantity, limit)})).data[0]
    _run(get_client().table("cart_item_flavors").insert(
        [{"cart_item_id": item["id"], "flavor_id": fid} for fid in design]))


def update_qty(line_id: str, quantity: int) -> None:
    """Change a line's quantity, capped at stock. 0 removes the line (US-304 AC1, AC2).

    Story: US-304 (U2-07).
    """
    if quantity <= 0:
        remove_line(line_id)
        return
    line = next((line for line in get_cart() if line.id == line_id), None)
    if line is None:
        return  # already gone
    quantity = min(quantity, max(max_quantity(line.base_chip, line.flavors), 1))

    if _user_id() is None:
        for raw in _guest_lines():
            if raw["id"] == line_id:
                raw["quantity"] = quantity
        return
    _run(get_client().table("cart_items").update({"quantity": quantity}).eq("id", line_id))


def remove_line(line_id: str) -> None:
    """Take a line out of the cart. Story: US-304 (U2-07)."""
    if _user_id() is None:
        st.session_state[GUEST_CART_KEY] = [line for line in _guest_lines() if line["id"] != line_id]
        return
    # Deleting the line also deletes its flavors (ON DELETE CASCADE).
    _run(get_client().table("cart_items").delete().eq("id", line_id))


def merge_guest_cart() -> None:
    """After sign-in, move guest lines into the saved cart; same bags add up, never above stock.

    Called from app/utils/session.py on_sign_in(). Story: US-305 (L-05).
    """
    guest_lines = list(st.session_state.get(GUEST_CART_KEY, []))
    if not guest_lines or _user_id() is None:
        return
    for line in guest_lines:
        try:
            add_bag(line["base_chip_id"], line["flavor_ids"], line["quantity"])
        except CartError as error:
            # A bag that's no longer possible (sold out, hidden) is skipped, not fatal.
            logger.warning("Skipped a guest bag while merging: %s", error)
    st.session_state[GUEST_CART_KEY] = []
