"""UI/UX requirements from doc 02 that code can check (the rest needs a real browser).

- S2: the "New" badge is honest (based on the real date added)
- S16 / NFR-REL-02: the offline message has a "Try again" button
- S5: "Place order" locks while placing, and unlocks with a clear message on a problem
- S6 / section 4: no moving celebration (reduce motion can't be detected)
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from conftest import db_error
from streamlit.testing.v1 import AppTest

from app.models.catalog import BaseChip

ENTRY_POINT = str(Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py")
NOW = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)


def _chip(added: datetime | None) -> BaseChip:
    return BaseChip("x", "Test Chip", "", "Classic", "Thin", 2, Decimal("2.50"), 10, created_at=added)


def _open(page: str, user=None) -> AppTest:
    at = AppTest.from_file(ENTRY_POINT, default_timeout=30)
    if user is not None:
        at.session_state["current_user"] = user
    at.switch_page(page).run()
    return at


# S2 "New" badge ------------------------------------------------------------------------

def test_new_badge_only_for_chips_added_in_the_last_14_days():
    assert _chip(NOW - timedelta(days=3)).is_new(now=NOW)
    assert _chip(NOW - timedelta(days=14)).is_new(now=NOW)
    assert not _chip(NOW - timedelta(days=15)).is_new(now=NOW)
    assert not _chip(None).is_new(now=NOW)  # unknown date: never claim "New"


# S16 / NFR-REL-02 Try again ---------------------------------------------------------------

def test_offline_message_has_a_try_again_button(fake_supabase):
    fake_supabase.offline = True

    at = _open("pages/shop.py")

    assert not at.exception, at.exception
    assert any("snack break" in w.value for w in at.warning)
    assert [b.label for b in at.button if b.label == "Try again"] == ["Try again"]


# S4 cart line image ------------------------------------------------------------------------

def test_cart_lines_show_a_picture_or_the_chip_icon(as_customer):
    at = _open("pages/cart.py", as_customer)

    assert not at.exception, at.exception
    # Kettle Cooked has a photo in the sample data; Wavy Ridge doesn't, so it gets the icon.
    assert len(at.get("image")) == 1
    assert any(":material/bakery_dining:" in m.value for m in at.markdown)


# S5 Place order locks, then unlocks with a clear message -------------------------------------

def test_place_order_unlocks_and_explains_when_something_sold_out(as_customer, fake_supabase):
    def sold_out(params):
        raise db_error("OUT_OF_STOCK: Not enough stock for: Sweet Potato (3 left, 4 needed)")

    fake_supabase.rpc_handlers["place_order"] = sold_out
    at = _open("pages/checkout.py", as_customer)

    next(b for b in at.button if b.label == "Place order").click().run()

    assert not at.exception, at.exception
    assert any("Sweet Potato (3 left, 4 needed)" in e.value for e in at.error)
    button = next(b for b in at.button if b.label in ("Place order", "Placing your order..."))
    assert button.label == "Place order" and not button.disabled  # unlocked again


def test_place_order_needs_name_and_address_and_stays_usable(as_customer, fake_supabase):
    at = _open("pages/checkout.py", as_customer)
    next(t for t in at.text_area if t.label == "Delivery address").input("   ")

    next(b for b in at.button if b.label == "Place order").click().run()

    assert any("delivery name and address" in e.value for e in at.error)
    assert not next(b for b in at.button if b.label == "Place order").disabled
    assert ("rpc", "place_order") not in fake_supabase.calls


# S6 / section 4: still celebration --------------------------------------------------------

def test_confirmation_celebrates_without_moving_balloons():
    source = (Path(ENTRY_POINT).parent / "pages" / "confirmation.py").read_text(encoding="utf-8")

    assert "st.balloons(" not in source and "st.snow(" not in source
