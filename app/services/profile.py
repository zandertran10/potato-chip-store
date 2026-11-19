"""Profile service: the signed-in customer's own display name and saved address.

Stub: the story fills in its function. The signature is the contract
(docs/architecture/service-contracts.md).
"""

from __future__ import annotations


def update_profile(display_name: str, default_address: str | None) -> None:
    """Save the caller's display name and default address. Checkout pre-fills the address.

    RLS lets users edit only these two columns of their own profile. Story: US-505 (U3-08).
    """
    raise NotImplementedError("US-505: update_profile")
