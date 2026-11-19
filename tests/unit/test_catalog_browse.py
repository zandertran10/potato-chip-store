"""Catalog stories: US-102 browse, US-103 search, US-104 filter, US-105 sort,
US-101 featured, US-601 staff picks, US-602 surprise me, settings."""

import random
from decimal import Decimal

import pytest
from conftest import BBQ, CINNAMON, KETTLE, SALT_VINEGAR, SEA_SALT, TRUFFLE

from app.models.catalog import SearchFilters
from app.services import catalog

# US-102 Browse the shop -------------------------------------------------------------

def test_list_base_chips_shows_active_chips_featured_first(fake_supabase):
    names = [chip.name for chip in catalog.list_base_chips()]

    assert names == ["Classic Thin", "Kettle Cooked", "Wavy Ridge", "Sweet Potato"]  # featured A-Z, then the rest
    assert "Retired Ripple" not in names  # hidden chips never appear (AC3)


def test_list_base_chips_for_staff_includes_hidden_ones(fake_supabase):
    names = [chip.name for chip in catalog.list_base_chips(include_inactive=True)]

    assert "Retired Ripple" in names


def test_list_flavors_groups_by_family_and_keeps_exact_prices(fake_supabase):
    flavors = catalog.list_flavors()

    assert len(flavors) == 10
    assert [f.family for f in flavors] == sorted(f.family for f in flavors)
    assert next(f for f in flavors if f.id == SEA_SALT).price == Decimal("0.25")


def test_catalog_unavailable_when_supabase_is_down(fake_supabase):
    fake_supabase.offline = True

    with pytest.raises(catalog.CatalogUnavailable):
        catalog.list_base_chips()


# US-103 Search ------------------------------------------------------------------------

def test_search_is_case_insensitive_and_matches_part_of_a_word(fake_supabase):
    results = catalog.search("bbq")  # AC2: "bbq" finds "Smoky BBQ"

    assert [f.name for f in results.flavors] == ["Smoky BBQ"]
    assert results.count == 1


def test_search_looks_at_chip_descriptions_too(fake_supabase):
    results = catalog.search("ORGANIC")

    assert len(results.chips) == 4  # every chip description says "organic"


def test_search_with_no_match_returns_nothing(fake_supabase):
    assert catalog.search("pizza").count == 0


# US-104 Filter ------------------------------------------------------------------------

def test_filters_work_together_with_the_search_word(fake_supabase):
    results = catalog.search("", SearchFilters(families=("Spicy",), max_heat=1))

    assert [f.name for f in results.flavors] == ["Smoky BBQ"]  # Chili Kick has heat 3


def test_in_stock_only_hides_sold_out_items(fake_supabase):
    results = catalog.search("", SearchFilters(in_stock_only=True))

    assert TRUFFLE not in [f.id for f in results.flavors]


def test_price_filter_uses_exact_money(fake_supabase):
    results = catalog.search("", SearchFilters(styles=("Kettle", "Wavy"), max_price=Decimal("2.75")))

    assert [c.name for c in results.chips] == ["Wavy Ridge"]


# US-105 Sort ----------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("sort", "first_chip"),
    [("price_asc", "Classic Thin"), ("price_desc", "Sweet Potato"), ("name", "Classic Thin"), ("newest", "Sweet Potato")],
)
def test_sort_options(fake_supabase, sort, first_chip):
    assert catalog.search("", sort=sort).chips[0].name == first_chip


# US-101 Home, US-601 Staff picks, US-602 Surprise me, settings -------------------------

def test_featured_chips_are_at_most_four(fake_supabase):
    featured = catalog.featured_chips()

    assert 1 <= len(featured) <= 4
    assert all(chip.is_featured for chip in featured)


def test_staff_picks_for_one_chip_include_their_flavors(fake_supabase):
    picks = catalog.list_staff_picks(KETTLE)

    assert len(picks) == 1
    assert set(picks[0].flavor_ids) == {SALT_VINEGAR, SEA_SALT}


def test_staff_picks_for_a_broken_id_is_empty(fake_supabase):
    assert catalog.list_staff_picks("not-an-id") == []


def test_random_combo_only_picks_in_stock_items_within_the_limit(fake_supabase):
    for seed in range(20):
        chip_id, flavor_ids = catalog.random_combo(rng=random.Random(seed))
        assert 1 <= len(flavor_ids) <= 3
        assert TRUFFLE not in flavor_ids  # sold out
        assert chip_id


def test_get_settings_uses_defaults_when_the_row_is_missing(fake_supabase):
    fake_supabase.tables["settings"] = []

    settings = catalog.get_settings()

    assert (settings.max_flavors, settings.low_stock_threshold) == (3, 10)


def test_unused_ids_stay_importable():
    # Keeps the shared ids in one place for the other test files.
    assert BBQ and CINNAMON
