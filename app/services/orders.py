"""Orders service: checkout, order history and the staff orders page.

Stubs: each story fills in its function. The signatures are the contract
(docs/architecture/service-contracts.md).
"""

from __future__ import annotations

from datetime import date

from app.models.orders import Order, PlacedOrder


def place_order(delivery_name: str, delivery_address: str, idempotency_key: str) -> PlacedOrder:
    """Call the place_order database function (migration 10) for the signed-in customer.

    Use one idempotency key per checkout attempt, kept in st.session_state, so a
    double click returns the same order. Turn OUT_OF_STOCK and the other error
    codes into friendly messages. Story: US-402 (L-03).
    """
    raise NotImplementedError("US-402: place_order")


def get_order(order_id: str) -> Order | None:
    """One order with its lines. None if it doesn't exist or isn't the caller's (RLS).

    Stories: US-403 (L-04), US-704 (L-07).
    """
    raise NotImplementedError("US-403: get_order")


def list_my_orders() -> list[Order]:
    """The signed-in customer's orders, newest first.

    Story: US-504 (L-06).
    """
    raise NotImplementedError("US-504: list_my_orders")


def list_all_orders(
    *, status: str | None = None, date_from: date | None = None, date_to: date | None = None
) -> list[Order]:
    """Every order for staff, filtered by status and date, newest first.

    Story: US-704 (L-07).
    """
    raise NotImplementedError("US-704: list_all_orders")


def set_status(order_id: str, status: str) -> None:
    """Staff move an order to packed or shipped. (Cancel uses cancel_order.)

    Story: US-704 (L-07).
    """
    raise NotImplementedError("US-704: set_status")


def cancel_order(order_id: str) -> None:
    """Staff cancel an order and its stock is put back.

    Needs a cancel_order database function (not written yet). Story: US-704 (L-07).
    """
    raise NotImplementedError("US-704: cancel_order")


def flavors_tried() -> set[str]:
    """Ids of every flavor the signed-in customer has ever ordered.

    Story: US-603 (U2-09).
    """
    raise NotImplementedError("US-603: flavors_tried")
