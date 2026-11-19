"""Orders service: checkout, order history and the staff orders page.

Placing and cancelling orders go through database functions (migrations 10
and 11), which run as one transaction each. Their coded errors
("OUT_OF_STOCK: ...") become OrderError with a friendly message.
The signatures are the contract (docs/architecture/service-contracts.md).
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import httpx
from postgrest.exceptions import APIError

from app.models.orders import ORDER_STATUSES, Order, OrderLine, PlacedOrder
from app.services import auth
from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)

CONNECTION_ERROR = "We couldn't reach the store. Nothing was charged. Please try again."

# What shoppers and staff see for each database error code.
_FRIENDLY = {
    "NOT_SIGNED_IN": "Please sign in to place an order.",
    "MISSING_KEY": "Something went wrong with this checkout. Please try again.",
    "MISSING_DELIVERY": "Please enter a delivery name and address.",
    "CART_EMPTY": "Your cart is empty.",
    "KEY_ALREADY_USED": "Something went wrong with this checkout. Please try again.",
    "TOO_MANY_ORDERS_TODAY": "The store has reached its daily order limit. Please try again tomorrow.",
    "NOT_ALLOWED": "You don't have permission to do that.",
    "NOT_FOUND": "That order doesn't exist.",
    "ALREADY_CANCELLED": "This order is already cancelled.",
    "ALREADY_SHIPPED": "A shipped order can no longer be cancelled.",
}


class OrderError(Exception):
    """A problem the page can show as is. `code` is the database's error code, if any."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code


def _db_error(error: APIError) -> OrderError:
    """Turn 'OUT_OF_STOCK: Not enough stock for: ...' into a friendly OrderError."""
    code, _, detail = (error.message or "").partition(": ")
    if code == "OUT_OF_STOCK":
        return OrderError(f"Some items just sold out. {detail}. Please update your cart and try again.", code)
    if code == "INVALID_BAG":
        return OrderError(detail or "One of your bags isn't valid any more.", code)
    if code in _FRIENDLY:
        return OrderError(_FRIENDLY[code], code)
    logger.error("Unexpected order error from the database")
    return OrderError("We couldn't complete that. Nothing was charged. Please try again.")


def _run(query):
    try:
        return query.execute()
    except APIError as error:
        raise _db_error(error) from None
    except httpx.HTTPError as error:
        logger.error("Orders query failed: %s", type(error).__name__)
        raise OrderError(CONNECTION_ERROR) from None


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True


def _money(value: Any) -> Decimal:
    return Decimal(str(value))


def _orders_with_lines(rows: list[dict], *, with_customer: bool = False) -> list[Order]:
    """Attach each order's lines (and, for staff, the customer's name and email)."""
    if not rows:
        return []
    order_ids = [row["id"] for row in rows]
    items = _run(get_client().table("order_items").select("*").in_("order_id", order_ids)).data or []
    item_flavors = []
    if items:
        item_flavors = _run(
            get_client().table("order_item_flavors").select("*").in_("order_item_id", [i["id"] for i in items])
        ).data or []
    customers: dict[str, dict] = {}
    if with_customer:
        user_ids = sorted({row["user_id"] for row in rows if row.get("user_id")})
        if user_ids:
            profiles = _run(get_client().table("profiles").select("id, display_name, email").in_("id", user_ids))
            customers = {p["id"]: p for p in profiles.data or []}

    orders = []
    for row in rows:
        lines = tuple(
            OrderLine(
                base_name=item["base_name"],
                base_price=_money(item["base_price"]),
                flavor_names=tuple(
                    sorted(f["flavor_name"] for f in item_flavors if f["order_item_id"] == item["id"])
                ),
                unit_price=_money(item["unit_price"]),
                quantity=int(item["quantity"]),
                line_total=_money(item["line_total"]),
            )
            for item in items
            if item["order_id"] == row["id"]
        )
        customer = customers.get(row.get("user_id"), {})
        orders.append(
            Order(
                id=row["id"],
                order_number=row["order_number"],
                status=row["status"],
                delivery_name=row["delivery_name"],
                delivery_address=row["delivery_address"],
                total=_money(row["total"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                lines=lines,
                customer_name=customer.get("display_name"),
                customer_email=customer.get("email"),
            )
        )
    return orders


def place_order(delivery_name: str, delivery_address: str, idempotency_key: str) -> PlacedOrder:
    """Call the place_order database function (migration 10) for the signed-in customer.

    Send one idempotency key per checkout attempt, kept in st.session_state, so a
    double click returns the same order (US-402 AC4). Raises OrderError with a
    friendly message, e.g. what ran out (US-402 AC2). Story: US-402 (L-03).
    """
    if not delivery_name.strip() or not delivery_address.strip():
        raise OrderError(_FRIENDLY["MISSING_DELIVERY"], "MISSING_DELIVERY")
    response = _run(
        get_client().rpc(
            "place_order",
            {
                "p_delivery_name": delivery_name.strip(),
                "p_delivery_address": delivery_address.strip(),
                "p_idempotency_key": idempotency_key,
            },
        )
    )
    data = response.data
    row = data[0] if isinstance(data, list) else data
    placed = PlacedOrder(
        order_id=row["order_id"],
        order_number=row["order_number"],
        total=_money(row["total"]),
        already_placed=bool(row["already_placed"]),
    )
    logger.info("Order placed: %s", placed.order_number)  # NFR-LOG-02, no personal data
    return placed


def get_order(order_id: str) -> Order | None:
    """One order with its lines. None if it doesn't exist or isn't the caller's (RLS).

    Staff also get the customer's name and email (US-704 AC2).
    Stories: US-403 (L-04), US-704 (L-07).
    """
    if not _is_uuid(order_id):
        return None
    response = _run(get_client().table("orders").select("*").eq("id", order_id).maybe_single())
    row = response.data if response else None
    if not row:
        return None
    user = auth.current_user()
    is_staff = user is not None and user.role in ("staff", "owner")
    # Customers only ever see their own orders (US-403 AC4); RLS enforces it too.
    if not is_staff and (user is None or row.get("user_id") != user.id):
        return None
    return _orders_with_lines([row], with_customer=is_staff)[0]


def list_my_orders() -> list[Order]:
    """The signed-in customer's orders, newest first. Story: US-504 (L-06)."""
    user = auth.current_user()
    if user is None:
        return []
    rows = _run(
        get_client().table("orders").select("*").eq("user_id", user.id).order("created_at", desc=True)
    ).data or []
    return _orders_with_lines(rows)


def list_all_orders(
    *, status: str | None = None, date_from: date | None = None, date_to: date | None = None
) -> list[Order]:
    """Every order for staff, filtered by status and date, newest first. Story: US-704 (L-07)."""
    query = get_client().table("orders").select("*")
    if status:
        query = query.eq("status", status)
    if date_from:
        query = query.gte("created_at", f"{date_from.isoformat()}T00:00:00+00:00")
    if date_to:
        query = query.lte("created_at", f"{date_to.isoformat()}T23:59:59.999999+00:00")
    rows = _run(query.order("created_at", desc=True)).data or []
    return _orders_with_lines(rows, with_customer=True)


def set_status(order_id: str, status: str) -> None:
    """Staff move an order to placed, packed or shipped. (Cancel uses cancel_order.)

    Story: US-704 (L-07).
    """
    if status not in ORDER_STATUSES or status == "cancelled":
        raise OrderError("Use Cancel to cancel an order, so its stock is put back.")
    if not _is_uuid(order_id):
        raise OrderError(_FRIENDLY["NOT_FOUND"], "NOT_FOUND")
    updated = _run(get_client().table("orders").update({"status": status}).eq("id", order_id)).data
    if not updated:
        # RLS returns nothing for non-staff, or the order doesn't exist.
        raise OrderError("That order couldn't be updated.", "NOT_FOUND")
    logger.info("Order status changed to %s", status)


def cancel_order(order_id: str) -> None:
    """Staff cancel an order and its stock is put back (migration 11). Story: US-704 (L-07)."""
    if not _is_uuid(order_id):
        raise OrderError(_FRIENDLY["NOT_FOUND"], "NOT_FOUND")
    _run(get_client().rpc("cancel_order", {"p_order_id": order_id}))
    logger.info("Order cancelled")


def flavors_tried() -> set[str]:
    """Ids of every flavor the signed-in customer has ordered (cancelled orders don't count).

    Story: US-603 (U2-09).
    """
    return {
        flavor_id
        for order in list_my_orders()
        if order.status != "cancelled"
        for flavor_id in _flavor_ids_in(order.id)
    }


def _flavor_ids_in(order_id: str) -> list[str]:
    items = _run(get_client().table("order_items").select("id").eq("order_id", order_id)).data or []
    if not items:
        return []
    rows = _run(
        get_client().table("order_item_flavors").select("flavor_id").in_("order_item_id", [i["id"] for i in items])
    ).data or []
    return [row["flavor_id"] for row in rows]
