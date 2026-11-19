"""Cart service: works for guests (cart in st.session_state) and customers (saved cart).

Stubs: each story fills in its function. The signatures are the contract
(docs/architecture/service-contracts.md).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.models.cart import CartLine


def get_cart() -> list[CartLine]:
    """Every line in the current cart (guest or signed-in customer).

    Story: US-303 (U2-06).
    """
    raise NotImplementedError("US-303: get_cart")


def count_bags() -> int:
    """Total number of bags in the cart, for the header badge.

    The header shows no count until this is filled in. Story: US-302 (U2-04).
    """
    raise NotImplementedError("US-302: count_bags")


def add_bag(base_chip_id: str, flavor_ids: Sequence[str], quantity: int) -> None:
    """Add a bag. The same base and flavors again raises that line's quantity (US-302 AC4).

    Never above the lowest stock of the chip and its flavors. Story: US-302 (U2-04).
    """
    raise NotImplementedError("US-302: add_bag")


def update_qty(line_id: str, quantity: int) -> None:
    """Change a line's quantity, capped at stock. 0 removes the line.

    Story: US-304 (U2-07).
    """
    raise NotImplementedError("US-304: update_qty")


def remove_line(line_id: str) -> None:
    """Take a line out of the cart.

    Story: US-304 (U2-07).
    """
    raise NotImplementedError("US-304: remove_line")


def merge_guest_cart() -> None:
    """After sign-in, move guest lines into the saved cart; same bags add up, never above stock.

    Called from app/utils/session.py on_sign_in(). Story: US-305 (L-05).
    """
    raise NotImplementedError("US-305: merge_guest_cart")
