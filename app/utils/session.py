"""Session hooks: things that happen at the moment someone signs in."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def on_sign_in() -> None:
    """Runs right after a successful sign-in or register (app/services/auth.py).

    Moves a guest's bags into their saved cart (US-305 AC2). A problem here must
    never stop someone signing in, so it is logged and skipped.
    """
    # Imported here, not at the top: cart imports auth, and auth imports this file.
    from app.services import cart

    try:
        cart.merge_guest_cart()
    except cart.CartError as error:
        logger.warning("Could not merge the guest cart: %s", error)
