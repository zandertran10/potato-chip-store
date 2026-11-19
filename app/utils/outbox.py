"""Order confirmation emails, saved as .eml files and never sent (BR-09, US-404)."""

from __future__ import annotations

import html
import re
from email.message import EmailMessage
from email.utils import format_datetime
from pathlib import Path

from app.models.orders import Order

_ORDER_NUMBER = re.compile(r"^CHIP-\d{8}-\d{4}$")


def _line_text(line) -> str:
    flavors = ", ".join(line.flavor_names)
    return f"{line.quantity} x {line.base_name} + {flavors} @ ${line.unit_price:.2f} = ${line.line_total:.2f}"


def build_confirmation_email(order: Order, to_email: str, from_email: str) -> EmailMessage:
    """The email as an EmailMessage: plain text plus a simple HTML version (US-404 AC2)."""
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = from_email
    message["Subject"] = f"Your order {order.order_number} is confirmed!"
    message["Date"] = format_datetime(order.created_at)

    lines = [_line_text(line) for line in order.lines]
    message.set_content(
        "\n".join(
            [
                f"Hi {order.delivery_name},",
                "",
                f"Thanks for your order {order.order_number}! Here's what we're packing:",
                "",
                *lines,
                "",
                f"Total: ${order.total:.2f}",
                "",
                f"Delivering to: {order.delivery_name}, {order.delivery_address}",
                "",
                "No payment was taken: this is a demo store.",
                "Potato Chip Co.",
            ]
        )
    )
    # Names and addresses are escaped, so nothing a customer typed can become HTML.
    items = "".join(f"<li>{html.escape(text)}</li>" for text in lines)
    message.add_alternative(
        f"""<p>Hi {html.escape(order.delivery_name)},</p>
<p>Thanks for your order <strong>{html.escape(order.order_number)}</strong>! Here's what we're packing:</p>
<ul>{items}</ul>
<p><strong>Total: ${order.total:.2f}</strong></p>
<p>Delivering to: {html.escape(order.delivery_name)}, {html.escape(order.delivery_address)}</p>
<p><em>No payment was taken: this is a demo store.</em></p>
<p>Potato Chip Co.</p>""",
        subtype="html",
    )
    return message


def write_confirmation_email(order: Order, to_email: str, from_email: str, outbox_dir: Path) -> Path:
    """Save outbox/order-<order number>.eml and return its path.

    Called only AFTER the order is saved. The caller logs any error and lets the
    order succeed anyway (NFR-DI-08). Story: US-404 (L-01).
    """
    # The file name uses only the order number, checked against its exact format,
    # so nothing else can sneak into the path.
    if not _ORDER_NUMBER.match(order.order_number):
        raise ValueError("Unexpected order number format")
    outbox_dir = Path(outbox_dir)
    outbox_dir.mkdir(parents=True, exist_ok=True)
    path = outbox_dir / f"order-{order.order_number}.eml"
    path.write_bytes(bytes(build_confirmation_email(order, to_email, from_email)))
    return path
