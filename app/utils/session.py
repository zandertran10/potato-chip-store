"""Session hooks: things that happen at the moment someone signs in."""

from __future__ import annotations


def on_sign_in() -> None:
    """Runs right after a successful sign-in or register (app/services/auth.py).

    Empty on purpose for now. Story US-305 (L-05) adds one line here:
        cart.merge_guest_cart()
    so a guest's bags move into their saved cart. It's empty until then because
    calling the unfinished cart service would break every sign-in.
    """
