"""Unit tests for app/services/catalog.py.

US-201 (U2-01): get_base_chip. Uses the fake Supabase from tests/conftest.py,
so no real database or keys are needed.
"""

from decimal import Decimal

import pytest

from app.services import catalog

KETTLE_ID = "00000000-0000-4000-8000-000000000102"
HIDDEN_CHIP_ID = "00000000-0000-4000-8000-000000000105"  # "Retired Ripple", is_active = false


def test_get_base_chip_returns_the_chip_with_all_its_facts(fake_supabase):
    """Happy path: a real id gives a BaseChip with exact money and the chip facts."""
    chip = catalog.get_base_chip(KETTLE_ID)

    assert chip is not None
    assert chip.name == "Kettle Cooked"
    assert chip.price == Decimal("3.00")  # exact money, not a float
    assert (chip.style, chip.thickness, chip.crunch_level) == ("Kettle", "Thick", 3)
    assert chip.stock == 80
    assert chip.image_path == "chips/kettle.webp"  # the storage path, not a URL


def test_get_base_chip_raises_catalog_unavailable_when_supabase_is_down(fake_supabase):
    """Error: a network failure becomes CatalogUnavailable, so the page can say so kindly."""
    fake_supabase.offline = True

    with pytest.raises(catalog.CatalogUnavailable):
        catalog.get_base_chip(KETTLE_ID)


@pytest.mark.parametrize(
    "bad_id",
    [
        HIDDEN_CHIP_ID,  # a hidden chip counts as "not found" (US-201 AC4)
        "00000000-0000-4000-8000-000000000999",  # a well-formed id that doesn't exist
        "abc",  # a broken link: not an id at all
        "",  # no ?id= in the link
    ],
)
def test_get_base_chip_returns_none_for_hidden_or_wrong_ids(fake_supabase, bad_id):
    """Edge cases: every kind of wrong or hidden id gives None, never a crash."""
    assert catalog.get_base_chip(bad_id) is None
