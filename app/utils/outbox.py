"""Order confirmation emails, saved as .eml files and never sent (BR-09)."""

from __future__ import annotations

from pathlib import Path

from app.models.orders import Order


def write_confirmation_email(order: Order, to_email: str, from_email: str, outbox_dir: Path) -> Path:
    """Save outbox/order-<order number>.eml and return its path.

    Built with email.message.EmailMessage: To, From, Subject "Your order <number>
    is confirmed!", date, greeting, items, total and a "no payment was taken
    (demo)" note (US-404 AC2). Called only AFTER the order is saved; if writing
    fails, log it and let the order still succeed (NFR-DI-08). Story: US-404 (L-01).
    """
    raise NotImplementedError("US-404: write_confirmation_email")
