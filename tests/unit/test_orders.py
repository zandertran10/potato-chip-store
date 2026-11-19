"""Checkout and orders: US-401/402 place order, US-403 confirmation, US-404 outbox email,
US-504 my orders, US-505 profile, US-603 flavor passport, US-704 staff orders."""

from datetime import date
from decimal import Decimal
from email import message_from_bytes, policy

import pytest
from conftest import CHILI, CUSTOMER_ID, LIME, SEA_SALT, SOUR_CREAM, _id, db_error

from app.components.flavor_passport import earned_badges
from app.services import orders, profile
from app.utils.outbox import write_confirmation_email

ORDER_1, ORDER_2 = _id(0x501), _id(0x502)  # shipped, placed (seed)


def _placed(params):
    return [{"order_id": "new-order", "order_number": "CHIP-20261118-0001", "total": 7.5, "already_placed": False}]


# US-402 Place the order ------------------------------------------------------------------

def test_place_order_calls_the_database_function_once(as_customer, fake_supabase):
    seen = []
    fake_supabase.rpc_handlers["place_order"] = lambda params: seen.append(params) or _placed(params)

    placed = orders.place_order("Casey", "12 Demo Lane", "key-1")

    assert placed.order_number == "CHIP-20261118-0001"
    assert placed.total == Decimal("7.5")
    assert seen == [{"p_delivery_name": "Casey", "p_delivery_address": "12 Demo Lane", "p_idempotency_key": "key-1"}]


def test_out_of_stock_explains_what_changed(as_customer, fake_supabase):
    def sold_out(params):
        raise db_error("OUT_OF_STOCK: Not enough stock for: Sweet Potato (3 left, 4 needed)")

    fake_supabase.rpc_handlers["place_order"] = sold_out

    with pytest.raises(orders.OrderError) as error:
        orders.place_order("Casey", "12 Demo Lane", "key-1")
    assert error.value.code == "OUT_OF_STOCK"
    assert "Sweet Potato (3 left, 4 needed)" in str(error.value)


@pytest.mark.parametrize(("name", "address"), [("", "12 Demo Lane"), ("Casey", "   ")])
def test_delivery_name_and_address_are_required(as_customer, fake_supabase, name, address):
    with pytest.raises(orders.OrderError, match="delivery name and address"):
        orders.place_order(name, address, "key-1")
    assert ("rpc", "place_order") not in fake_supabase.calls  # never reached the database


def test_place_order_offline_says_nothing_was_charged(as_customer, fake_supabase):
    fake_supabase.offline = True

    with pytest.raises(orders.OrderError, match="Nothing was charged"):
        orders.place_order("Casey", "12 Demo Lane", "key-1")


# US-403 / US-504 Seeing orders --------------------------------------------------------------

def test_my_orders_are_newest_first_with_their_lines(as_customer):
    my_orders = orders.list_my_orders()

    assert [o.order_number for o in my_orders] == ["CHIP-20261110-0001", "CHIP-20261101-0001"]
    assert my_orders[1].lines[1].flavor_names == ("Chili Kick", "Zesty Lime")
    assert my_orders[1].total == Decimal("9.25")


def test_a_customer_cannot_open_someone_elses_order(as_customer, fake_supabase):
    fake_supabase.tables["orders"][0]["user_id"] = "someone-else"

    assert orders.get_order(ORDER_1) is None  # US-403 AC4
    assert orders.get_order("CHIP-20261101-0001") is None  # not an id at all


def test_staff_see_any_order_with_the_customer_email(as_staff):
    order = orders.get_order(ORDER_2)

    assert order.customer_email == "customer@demo.test"


def test_guests_see_no_orders(fake_supabase):
    assert orders.list_my_orders() == []


# US-704 Staff orders -------------------------------------------------------------------------

def test_staff_filter_orders_by_status_and_date(as_staff):
    assert [o.order_number for o in orders.list_all_orders(status="placed")] == ["CHIP-20261110-0001"]
    assert len(orders.list_all_orders(date_from=date(2026, 11, 5))) == 1
    assert len(orders.list_all_orders(date_to=date(2026, 11, 5))) == 1


def test_status_can_move_on_but_cancel_needs_cancel_order(as_staff, fake_supabase):
    orders.set_status(ORDER_2, "packed")
    assert fake_supabase.rows("orders")[1]["status"] == "packed"

    with pytest.raises(orders.OrderError, match="Use Cancel"):
        orders.set_status(ORDER_2, "cancelled")


def test_cancelling_a_shipped_order_is_refused_clearly(as_staff, fake_supabase):
    def shipped(params):
        raise db_error("ALREADY_SHIPPED: A shipped order can no longer be cancelled.")

    fake_supabase.rpc_handlers["cancel_order"] = shipped

    with pytest.raises(orders.OrderError, match="no longer be cancelled"):
        orders.cancel_order(ORDER_1)


# US-603 Flavor passport ---------------------------------------------------------------------

def test_flavors_tried_skip_cancelled_orders(as_customer, fake_supabase):
    assert orders.flavors_tried() == {SEA_SALT, LIME, CHILI, SOUR_CREAM}

    fake_supabase.tables["orders"][1]["status"] = "cancelled"  # the Sour Cream order
    assert SOUR_CREAM not in orders.flavors_tried()


@pytest.mark.parametrize(("tried", "badges"), [(0, []), (3, ["Taster"]), (6, ["Taster", "Explorer"]),
                                               (10, ["Taster", "Explorer", "Flavor Master"])])
def test_passport_badges(tried, badges):
    assert earned_badges(tried, 10) == badges


# US-404 Confirmation email ------------------------------------------------------------------

def test_confirmation_email_is_a_real_eml_file(as_customer, tmp_path):
    order = orders.get_order(ORDER_1)

    path = write_confirmation_email(order, "customer@demo.test", "orders@potatochipco.test", tmp_path / "outbox")

    assert path.name == "order-CHIP-20261101-0001.eml"
    email = message_from_bytes(path.read_bytes(), policy=policy.default)
    assert email["Subject"] == "Your order CHIP-20261101-0001 is confirmed!"
    assert email["To"] == "customer@demo.test"
    body = email.get_body(("plain",)).get_content()
    assert "Total: $9.25" in body and "No payment was taken" in body


def test_confirmation_email_escapes_html_typed_by_customers(as_customer, fake_supabase, tmp_path):
    fake_supabase.tables["orders"][0]["delivery_name"] = "<b>Casey</b>"
    order = orders.get_order(ORDER_1)

    path = write_confirmation_email(order, "customer@demo.test", "orders@potatochipco.test", tmp_path)

    html = message_from_bytes(path.read_bytes(), policy=policy.default).get_body(("html",)).get_content()
    assert "&lt;b&gt;Casey&lt;/b&gt;" in html and "<b>Casey</b>" not in html


# US-505 Profile ---------------------------------------------------------------------------------

def test_profile_update_saves_and_checkout_gets_the_address(as_customer, fake_supabase):
    profile.update_profile("Casey C", "1 New Street")

    assert profile.get_default_address() == "1 New Street"
    row = next(r for r in fake_supabase.rows("profiles") if r["id"] == CUSTOMER_ID)
    assert row["display_name"] == "Casey C"


def test_profile_needs_a_name(as_customer):
    with pytest.raises(profile.ProfileError, match="display name"):
        profile.update_profile("  ", None)
