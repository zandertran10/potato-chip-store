"""Store Admin stories: US-701 chips, US-702 flavors and staff picks, US-703 stock,
US-705 staff, US-706 settings, US-707 dashboard. (US-704 orders: test_orders.py.)"""

import dataclasses
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from conftest import (
    BBQ,
    CHEDDAR,
    CUSTOMER_ID,
    KETTLE,
    SEA_SALT,
    STAFF_ID,
    WAVY,
    db_error,
)

from app.models.catalog import BaseChip, StoreSettings
from app.services import admin, catalog

NEW_CHIP = BaseChip(id="", name="Rippled Rosemary", description="Herby and crisp.", style="Wavy",
                    thickness="Regular", crunch_level=2, price=Decimal("3.10"), stock=25)


# US-701 Base chips ------------------------------------------------------------------------

def test_adding_a_chip_saves_its_starting_stock(as_staff, fake_supabase):
    saved = admin.save_base_chip(NEW_CHIP)

    assert saved.id and saved.name == "Rippled Rosemary"
    row = next(r for r in fake_supabase.rows("base_chips") if r["id"] == saved.id)
    assert row["stock"] == 25 and row["price"] == "3.10"


def test_editing_a_chip_never_changes_stock(as_staff, fake_supabase):
    kettle = catalog.get_base_chip(KETTLE)

    admin.save_base_chip(dataclasses.replace(kettle, price=Decimal("3.20"), stock=999))

    row = next(r for r in fake_supabase.rows("base_chips") if r["id"] == KETTLE)
    assert row["price"] == "3.20" and row["stock"] == 80  # stock only changes through set_stock


def test_hiding_a_chip_keeps_it_but_takes_it_out_of_the_shop(as_staff):
    admin.save_base_chip(dataclasses.replace(catalog.get_base_chip(KETTLE), is_active=False))

    assert catalog.get_base_chip(KETTLE) is None
    assert any(c.id == KETTLE for c in catalog.list_base_chips(include_inactive=True))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"price": Decimal(0)}, "above 0"),
        ({"price": Decimal("2.505")}, "2 decimals"),
        ({"stock": -1}, "0 or more"),
        ({"name": "  "}, "Name is required"),
        ({"image_path": "products/x.webp", "image_alt": ""}, "alt text"),
    ],
)
def test_chip_checks(as_staff, change, message):
    with pytest.raises(admin.AdminError, match=message):
        admin.save_base_chip(dataclasses.replace(NEW_CHIP, **change))


def test_duplicate_names_get_a_clear_message(as_staff, fake_supabase, monkeypatch):
    def duplicate(*args, **kwargs):
        raise admin.APIError({"message": "duplicate key", "code": "23505", "hint": None, "details": None})

    monkeypatch.setattr("conftest._FakeQuery.execute", duplicate)

    with pytest.raises(admin.AdminError, match="already used"):
        admin.save_base_chip(NEW_CHIP)


@pytest.mark.parametrize(
    ("size", "content_type", "ok"),
    [(100, "image/webp", True), (100, "image/gif", False),
     (2 * 1024 * 1024 + 1, "image/png", False), (0, "image/png", False)],
)
def test_image_upload_rules(as_staff, fake_supabase, size, content_type, ok):
    data = b"x" * size  # built here: pytest can't hold 2 MB in a test name
    if ok:
        path = admin.upload_image("../../secret.webp", data, content_type)
        assert path.startswith("products/") and path.endswith(".webp") and "secret" not in path
        assert path in fake_supabase.uploads
    else:
        with pytest.raises(admin.AdminError):
            admin.upload_image("photo", data, content_type)


# US-702 Flavors and staff picks -------------------------------------------------------------

def test_flavor_profile_scores_must_be_0_to_3(as_staff):
    flavor = next(f for f in catalog.list_flavors() if f.id == BBQ)

    with pytest.raises(admin.AdminError, match="Heat must be 0 to 3"):
        admin.save_flavor(dataclasses.replace(flavor, heat=4))


def test_staff_pick_is_replaced_and_can_be_removed(as_staff):
    admin.save_staff_pick(WAVY, 1, "Salt and Cheese", [SEA_SALT, CHEDDAR])

    [pick] = catalog.list_staff_picks(WAVY)
    assert pick.title == "Salt and Cheese" and set(pick.flavor_ids) == {SEA_SALT, CHEDDAR}

    admin.save_staff_pick(WAVY, 1, "", [])
    assert catalog.list_staff_picks(WAVY) == []


def test_staff_pick_needs_1_to_3_flavors_and_a_slot(as_staff):
    with pytest.raises(admin.AdminError, match="1 to 3 flavors"):
        admin.save_staff_pick(KETTLE, 2, "Too much", [SEA_SALT, BBQ, CHEDDAR, "x"])
    with pytest.raises(admin.AdminError, match="1, 2 and 3"):
        admin.save_staff_pick(KETTLE, 4, "Fourth", [SEA_SALT])


# US-703 Stock --------------------------------------------------------------------------------

def test_set_stock_calls_the_database_function(as_staff, fake_supabase):
    seen = []
    fake_supabase.rpc_handlers["set_stock"] = lambda params: seen.append(params)

    admin.set_stock("base", KETTLE, 120, " Restocked ")

    assert seen == [{"p_item_type": "base", "p_item_id": KETTLE, "p_new_stock": 120, "p_reason": "Restocked"}]


@pytest.mark.parametrize(("stock", "reason", "message"),
                         [(5, " ", "reason"), (-2, "count", "0 or more")])
def test_set_stock_needs_a_reason_and_a_valid_number(as_staff, fake_supabase, stock, reason, message):
    with pytest.raises(admin.AdminError, match=message):
        admin.set_stock("base", KETTLE, stock, reason)
    assert ("rpc", "set_stock") not in fake_supabase.calls


def test_stock_history_names_the_item_and_the_person(as_staff, fake_supabase):
    fake_supabase.tables["stock_history"] = [
        {"id": "h1", "item_type": "base", "item_id": KETTLE, "change": 20, "reason": "Restock",
         "order_id": None, "changed_by": STAFF_ID, "created_at": "2026-11-17T09:00:00+00:00"}]

    [change] = admin.stock_history()

    assert (change.item_name, change.change, change.changed_by_name) == ("Kettle Cooked", 20, "Sam Staff")


# US-705 Staff ----------------------------------------------------------------------------------

def test_owner_finds_a_user_by_email(as_owner):
    person = admin.find_user("  Customer@Demo.test ")

    assert person.id == CUSTOMER_ID and person.role == "customer"
    assert admin.find_user("nobody@demo.test") is None
    assert admin.find_user("not an email") is None


def test_set_role_only_hands_out_customer_or_staff(as_owner, fake_supabase):
    with pytest.raises(admin.AdminError, match="customer or staff"):
        admin.set_role(CUSTOMER_ID, "owner")


def test_the_database_refusal_is_shown_plainly(as_staff, fake_supabase):
    def refuse(params):
        raise db_error("NOT_ALLOWED: Only the store owner can change roles.")

    fake_supabase.rpc_handlers["set_role"] = refuse

    with pytest.raises(admin.AdminError, match="permission"):
        admin.set_role(CUSTOMER_ID, "staff")


# US-706 Settings, US-707 Dashboard ---------------------------------------------------------------

def test_settings_are_saved_and_checked(as_owner, fake_supabase):
    admin.save_settings(StoreSettings(max_flavors=4, low_stock_threshold=5, from_email="hello@potatochipco.test"))
    assert catalog.get_settings().max_flavors == 4

    with pytest.raises(admin.AdminError, match="1 to 5"):
        admin.save_settings(StoreSettings(max_flavors=6))
    with pytest.raises(admin.AdminError, match="valid"):
        admin.save_settings(StoreSettings(from_email="nope"))


def test_dashboard_numbers(as_owner, fake_supabase):
    stats = admin.dashboard_stats(now=datetime(2026, 11, 10, 20, 0, tzinfo=UTC))

    assert stats.orders_today == 1  # CHIP-20261110-0001
    assert stats.bags_this_week == 1  # only that order is within 7 days
    assert stats.low_stock_items == 2  # Sweet Potato (3 left) and Truffle Herb (0); threshold 10
    assert stats.top_flavors[0] == ("Sea Salt", 2)  # 2 bags of Classic + Sea Salt
