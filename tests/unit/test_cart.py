"""Cart stories: US-301/302 add a bag, US-303 view, US-304 change/remove,
US-305 keep the cart on sign-in, plus the pricing rules (BR-01, BR-02, US-203)."""

from decimal import Decimal

import pytest
from conftest import (
    BBQ,
    CHEDDAR,
    CHILI,
    CINNAMON,
    KETTLE,
    LIME,
    SALT_VINEGAR,
    SEA_SALT,
    SWEET,
    TRUFFLE,
    WAVY,
)

from app.services import auth, cart
from app.utils.pricing import bag_price, check_flavor_limit, combined_allergens

# Pricing rules ---------------------------------------------------------------------------

def test_bag_price_is_base_plus_each_flavor(sample_chips, sample_flavors):
    kettle = next(c for c in sample_chips if c.id == KETTLE)
    picked = [f for f in sample_flavors if f.id in (SEA_SALT, SALT_VINEGAR)]

    assert bag_price(kettle, picked) == Decimal("3.75")  # 3.00 + 0.25 + 0.50


@pytest.mark.parametrize(("chosen", "ok"), [(0, False), (1, True), (3, True), (4, False)])
def test_flavor_limit(chosen, ok):
    assert (check_flavor_limit(chosen, 3) is None) is ok


def test_allergens_are_combined_without_duplicates(sample_chips, sample_flavors):
    kettle = next(c for c in sample_chips if c.id == KETTLE)
    picked = [f for f in sample_flavors if f.name in ("Sour Cream & Onion", "Cheddar Blast", "Smoky BBQ")]

    assert combined_allergens(kettle, picked) == ["milk", "soy"]


# Guest cart (US-302, US-303, US-304) -------------------------------------------------------

def test_guest_adds_a_bag_and_sees_it_in_the_cart(fake_supabase):
    cart.add_bag(KETTLE, [SEA_SALT, SALT_VINEGAR], 2)

    lines = cart.get_cart()
    assert len(lines) == 1
    assert lines[0].quantity == 2
    assert lines[0].line_total == Decimal("7.50")
    assert cart.count_bags() == 2


def test_same_bag_again_raises_the_quantity_instead_of_a_new_line(fake_supabase):
    cart.add_bag(KETTLE, [SEA_SALT], 1)
    cart.add_bag(KETTLE, [SEA_SALT], 2)  # same design, flavors in any order

    assert [line.quantity for line in cart.get_cart()] == [3]


def test_quantity_never_goes_above_stock(fake_supabase):
    cart.add_bag(SWEET, [CINNAMON], 10)  # Sweet Potato has only 3

    assert cart.get_cart()[0].quantity == 3


@pytest.mark.parametrize(
    ("flavors", "message"),
    [
        ([], "at least 1 flavor"),
        ([SEA_SALT, LIME, CHILI, BBQ], "3 flavors max"),
        ([TRUFFLE], "Sold out"),
    ],
)
def test_invalid_bags_are_refused_with_a_clear_message(fake_supabase, flavors, message):
    with pytest.raises(cart.CartError, match=message):
        cart.add_bag(KETTLE, flavors, 1)
    assert cart.get_cart() == []


def test_update_quantity_and_zero_removes_the_line(fake_supabase):
    cart.add_bag(WAVY, [BBQ], 1)
    line_id = cart.get_cart()[0].id

    cart.update_qty(line_id, 5)
    assert cart.get_cart()[0].quantity == 5
    cart.update_qty(line_id, 0)
    assert cart.get_cart() == []


# Signed-in cart (US-303 AC3, US-305) -------------------------------------------------------

def test_signed_in_customer_sees_their_saved_cart(as_customer):
    lines = cart.get_cart()

    assert [line.base_chip.name for line in lines] == ["Kettle Cooked", "Wavy Ridge"]
    assert cart.count_bags() == 3


def test_signed_in_add_writes_a_new_line_to_the_database(as_customer, fake_supabase):
    cart.add_bag(SWEET, [CINNAMON], 1)

    assert len(fake_supabase.rows("cart_items")) == 3
    assert {"cart_item_id": fake_supabase.rows("cart_items")[-1]["id"], "flavor_id": CINNAMON} in fake_supabase.rows(
        "cart_item_flavors")


def test_remove_line_deletes_it_and_its_flavors(as_customer, fake_supabase):
    first = cart.get_cart()[0]

    cart.remove_line(first.id)

    assert first.id not in [line.id for line in cart.get_cart()]
    assert all(row["cart_item_id"] != first.id for row in fake_supabase.rows("cart_item_flavors"))


def test_guest_cart_is_merged_on_sign_in(fake_supabase):
    # As a guest: the same bag the customer already saved (Kettle + S&V + Sea Salt, x2), plus a new one.
    cart.add_bag(KETTLE, [SALT_VINEGAR, SEA_SALT], 1)
    cart.add_bag(WAVY, [CHEDDAR], 1)

    auth.sign_in("customer@demo.test", fake_supabase.test_password)  # runs on_sign_in()

    quantities = {(line.base_chip.name, tuple(f.name for f in line.flavors)): line.quantity for line in cart.get_cart()}
    assert quantities[("Kettle Cooked", ("Salt & Vinegar", "Sea Salt"))] == 3  # 2 saved + 1 guest
    assert quantities[("Wavy Ridge", ("Cheddar Blast",))] == 1
    assert cart.count_bags() == 5


def test_cart_problems_become_a_friendly_error(as_customer, fake_supabase):
    fake_supabase.offline = True

    with pytest.raises(cart.CartError, match="couldn't reach the store"):
        cart.get_cart()
