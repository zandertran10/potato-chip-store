"""Shared test setup: a fake Supabase client and sample data.

Unit tests never touch a real Supabase project or real keys. The fake client
answers the same calls the app makes, using sample data that matches the demo
seed (supabase/seed/*.sql and docs/deployment/demo-accounts.md):

- tables: select / eq / in_ / gte / lte / order / limit / maybe_single,
  plus insert / update / delete
- database functions: rpc(name, params), answered by handlers a test sets in
  `fake_supabase.rpc_handlers`
- sign-in, sign-up, sign-out and password-reset emails
- image uploads and public image URLs

It does NOT enforce the database's RLS rules; those are tested in SQL
(supabase/tests/). Services must filter by user themselves anyway.

How to use it in a test:

    def test_something(fake_supabase):             # the app now talks to the fake
        user = auth.sign_in("customer@demo.test", fake_supabase.test_password)
        fake_supabase.rows("orders")                # look at a table afterwards
"""

from __future__ import annotations

import copy
import sys
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

# Let tests `import app...` from the repo root, however pytest is started.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# These imports must stay BELOW the path fix above, or `app` can't be found.
import httpx
import streamlit as st
from postgrest.exceptions import APIError
from supabase_auth.errors import AuthApiError

from app.models.catalog import BaseChip, Flavor
from app.services.auth import CurrentUser

# Test-only password for the FAKE client. It is not a real demo password; those
# are never written in the repo (docs/deployment/demo-accounts.md).
FAKE_PASSWORD = "TestOnly123"


def _id(n: int) -> str:
    """Readable fixed ids, the same ones the seed files use."""
    return f"00000000-0000-4000-8000-{n:012x}" if n > 0xFFF else f"00000000-0000-4000-8000-000000000{n:03x}"


# --- Sample data (matches supabase/seed) ------------------------------------------

OWNER_ID, STAFF_ID, CUSTOMER_ID = (
    "00000000-0000-4000-8000-0000000000a1",
    "00000000-0000-4000-8000-0000000000a2",
    "00000000-0000-4000-8000-0000000000a3",
)

CLASSIC, KETTLE, WAVY, SWEET, RETIRED = (
    "00000000-0000-4000-8000-000000000101",
    "00000000-0000-4000-8000-000000000102",
    "00000000-0000-4000-8000-000000000103",
    "00000000-0000-4000-8000-000000000104",
    "00000000-0000-4000-8000-000000000105",  # hidden chip
)
SEA_SALT, SALT_VINEGAR, SOUR_CREAM, BBQ, CHEDDAR, LIME, CHILI, HONEY, CINNAMON, TRUFFLE = (
    f"00000000-0000-4000-8000-000000000{n}" for n in range(201, 211)
)
HIDDEN_CHIP_ID = RETIRED


def _chip_row(chip_id, name, style, thickness, crunch, price, stock, **extra) -> dict:
    row = {
        "id": chip_id, "name": name, "description": f"{name}: made by hand from organic potatoes.",
        "style": style, "thickness": thickness, "crunch_level": crunch, "allergens": [],
        "price": price, "stock": stock, "image_path": None, "image_alt": None,
        "is_featured": False, "is_active": True, "created_at": "2026-11-01T10:00:00+00:00",
    }
    row.update(extra)
    return row


def _flavor_row(flavor_id, name, family, salty, tangy, sweet, heat, price, stock, allergens=(), **extra) -> dict:
    row = {
        "id": flavor_id, "name": name, "description": f"{name} seasoning.", "family": family,
        "salty": salty, "tangy": tangy, "sweet": sweet, "heat": heat, "allergens": list(allergens),
        "price": price, "stock": stock, "icon": None, "is_active": True,
        "created_at": "2026-11-01T10:00:00+00:00",
    }
    row.update(extra)
    return row


def sample_tables() -> dict[str, list[dict]]:
    """A fresh copy of every table, as the seed leaves the database."""
    return {
        "profiles": [
            {"id": OWNER_ID, "email": "owner@demo.test", "display_name": "Olive Owner",
             "role": "owner", "default_address": None},
            {"id": STAFF_ID, "email": "staff@demo.test", "display_name": "Sam Staff",
             "role": "staff", "default_address": None},
            {"id": CUSTOMER_ID, "email": "customer@demo.test", "display_name": "Casey Customer",
             "role": "customer", "default_address": "12 Demo Lane, Springfield"},
        ],
        "base_chips": [
            _chip_row(CLASSIC, "Classic Thin", "Classic", "Thin", 2, 2.5, 100, is_featured=True),
            _chip_row(KETTLE, "Kettle Cooked", "Kettle", "Thick", 3, 3.0, 80, is_featured=True,
                      image_path="chips/kettle.webp", image_alt="A bowl of thick kettle chips",
                      created_at="2026-11-02T10:00:00+00:00"),
            _chip_row(WAVY, "Wavy Ridge", "Wavy", "Regular", 2, 2.75, 60, is_featured=True),
            _chip_row(SWEET, "Sweet Potato", "Sweet potato", "Regular", 1, 3.25, 3,
                      created_at="2026-11-03T10:00:00+00:00"),
            _chip_row(RETIRED, "Retired Ripple", "Wavy", "Thick", 2, 2.95, 0, is_active=False),
        ],
        "flavors": [
            _flavor_row(SEA_SALT, "Sea Salt", "Salty", 3, 0, 0, 0, 0.25, 200),
            _flavor_row(SALT_VINEGAR, "Salt & Vinegar", "Tangy", 2, 3, 0, 0, 0.5, 150),
            _flavor_row(SOUR_CREAM, "Sour Cream & Onion", "Herby", 1, 1, 0, 0, 0.5, 150, ["milk"]),
            _flavor_row(BBQ, "Smoky BBQ", "Spicy", 1, 1, 2, 1, 0.5, 120, ["soy"]),
            _flavor_row(CHEDDAR, "Cheddar Blast", "Salty", 2, 0, 0, 0, 0.6, 100, ["milk"]),
            _flavor_row(LIME, "Zesty Lime", "Tangy", 1, 3, 0, 0, 0.4, 90),
            _flavor_row(CHILI, "Chili Kick", "Spicy", 1, 0, 0, 3, 0.6, 70),
            _flavor_row(HONEY, "Honey Mustard", "Sweet", 1, 1, 2, 1, 0.6, 50, ["mustard"]),
            _flavor_row(CINNAMON, "Cinnamon Sugar", "Sweet", 0, 0, 3, 0, 0.5, 40),
            _flavor_row(TRUFFLE, "Truffle Herb", "Herby", 1, 0, 0, 0, 0.9, 0, ["milk"]),
        ],
        "staff_picks": [
            {"id": _id(0x301), "base_chip_id": KETTLE, "title": "Tangy Crunch", "position": 1},
            {"id": _id(0x302), "base_chip_id": WAVY, "title": "BBQ Cheddar Wave", "position": 1},
            {"id": _id(0x303), "base_chip_id": SWEET, "title": "Sweet Treat", "position": 1},
        ],
        "staff_pick_flavors": [
            {"staff_pick_id": _id(0x301), "flavor_id": SALT_VINEGAR},
            {"staff_pick_id": _id(0x301), "flavor_id": SEA_SALT},
            {"staff_pick_id": _id(0x302), "flavor_id": BBQ},
            {"staff_pick_id": _id(0x302), "flavor_id": CHEDDAR},
            {"staff_pick_id": _id(0x303), "flavor_id": CINNAMON},
        ],
        "settings": [{"id": 1, "max_flavors": 3, "low_stock_threshold": 10,
                      "from_email": "orders@potatochipco.test"}],
        "carts": [{"id": _id(0x901), "user_id": CUSTOMER_ID}],
        "cart_items": [
            {"id": _id(0x801), "cart_id": _id(0x901), "base_chip_id": KETTLE, "quantity": 2,
             "created_at": "2026-11-15T10:00:00+00:00"},
            {"id": _id(0x802), "cart_id": _id(0x901), "base_chip_id": WAVY, "quantity": 1,
             "created_at": "2026-11-15T10:01:00+00:00"},
        ],
        "cart_item_flavors": [
            {"cart_item_id": _id(0x801), "flavor_id": SALT_VINEGAR},
            {"cart_item_id": _id(0x801), "flavor_id": SEA_SALT},
            {"cart_item_id": _id(0x802), "flavor_id": BBQ},
        ],
        "orders": [
            {"id": _id(0x501), "order_number": "CHIP-20261101-0001", "user_id": CUSTOMER_ID,
             "status": "shipped", "delivery_name": "Casey Customer",
             "delivery_address": "12 Demo Lane, Springfield", "total": 9.25,
             "idempotency_key": _id(0x701), "created_at": "2026-11-01T15:30:00+00:00"},
            {"id": _id(0x502), "order_number": "CHIP-20261110-0001", "user_id": CUSTOMER_ID,
             "status": "placed", "delivery_name": "Casey Customer",
             "delivery_address": "12 Demo Lane, Springfield", "total": 3.5,
             "idempotency_key": _id(0x702), "created_at": "2026-11-10T18:05:00+00:00"},
        ],
        "order_items": [
            {"id": _id(0x601), "order_id": _id(0x501), "base_chip_id": CLASSIC, "base_name": "Classic Thin",
             "base_price": 2.5, "unit_price": 2.75, "quantity": 2, "line_total": 5.5},
            {"id": _id(0x602), "order_id": _id(0x501), "base_chip_id": WAVY, "base_name": "Wavy Ridge",
             "base_price": 2.75, "unit_price": 3.75, "quantity": 1, "line_total": 3.75},
            {"id": _id(0x603), "order_id": _id(0x502), "base_chip_id": KETTLE, "base_name": "Kettle Cooked",
             "base_price": 3.0, "unit_price": 3.5, "quantity": 1, "line_total": 3.5},
        ],
        "order_item_flavors": [
            {"order_item_id": _id(0x601), "flavor_id": SEA_SALT, "flavor_name": "Sea Salt", "flavor_price": 0.25},
            {"order_item_id": _id(0x602), "flavor_id": LIME, "flavor_name": "Zesty Lime", "flavor_price": 0.4},
            {"order_item_id": _id(0x602), "flavor_id": CHILI, "flavor_name": "Chili Kick", "flavor_price": 0.6},
            {"order_item_id": _id(0x603), "flavor_id": SOUR_CREAM, "flavor_name": "Sour Cream & Onion",
             "flavor_price": 0.5},
        ],
        "stock_history": [],
    }


# Tables whose rows are deleted along with their parent (ON DELETE CASCADE).
_CASCADES = {
    "cart_items": ("cart_item_flavors", "cart_item_id"),
    "staff_picks": ("staff_pick_flavors", "staff_pick_id"),
}
# Tables that get an id / created_at automatically on insert.
_NO_ID_TABLES = {"cart_item_flavors", "staff_pick_flavors", "order_item_flavors"}


# --- The fake Supabase client -----------------------------------------------------

class _FakeQuery:
    def __init__(self, fake: FakeSupabase, table: str):
        self._fake, self._table = fake, table
        self._filters: list = []
        self._order: list[tuple[str, bool]] = []
        self._limit: int | None = None
        self._single = False
        self._action = "select"
        self._payload = None

    # Reading ---------------------------------------------------------------
    def select(self, *_columns, **_options):
        return self

    def eq(self, column, value):
        self._filters.append(lambda row: row.get(column) == value)
        return self

    def in_(self, column, values):
        values = list(values)
        self._filters.append(lambda row: row.get(column) in values)
        return self

    def gte(self, column, value):
        self._filters.append(lambda row: row.get(column) is not None and str(row.get(column)) >= str(value))
        return self

    def lte(self, column, value):
        self._filters.append(lambda row: row.get(column) is not None and str(row.get(column)) <= str(value))
        return self

    def order(self, column, *, desc=False, **_options):
        self._order.append((column, desc))
        return self

    def limit(self, count):
        self._limit = count
        return self

    def maybe_single(self):
        self._single = True
        return self

    # Writing ---------------------------------------------------------------
    def insert(self, rows):
        self._action, self._payload = "insert", rows
        return self

    def update(self, values):
        self._action, self._payload = "update", values
        return self

    def delete(self):
        self._action = "delete"
        return self

    def execute(self):
        # Like the real client, the network is only touched when a query runs.
        if self._fake.offline:
            raise httpx.ConnectError("Supabase is unreachable (fake)")
        self._fake.calls.append((self._action, self._table))
        rows = self._fake.tables.setdefault(self._table, [])
        if self._action == "insert":
            return SimpleNamespace(data=self._insert(rows))
        matches = [row for row in rows if all(test(row) for test in self._filters)]
        if self._action == "update":
            for row in matches:
                row.update(copy.deepcopy(self._payload))
            return SimpleNamespace(data=copy.deepcopy(matches))
        if self._action == "delete":
            for row in matches:
                rows.remove(row)
                if self._table in _CASCADES:
                    child, column = _CASCADES[self._table]
                    self._fake.tables[child] = [r for r in self._fake.tables.get(child, []) if r[column] != row["id"]]
            return SimpleNamespace(data=copy.deepcopy(matches))
        for column, desc in reversed(self._order):
            matches.sort(key=lambda row: (row.get(column) is None, row.get(column)), reverse=desc)
        if self._limit is not None:
            matches = matches[: self._limit]
        matches = copy.deepcopy(matches)
        if self._single:
            # Like the real client: None when nothing matches.
            return SimpleNamespace(data=matches[0]) if matches else None
        return SimpleNamespace(data=matches)

    def _insert(self, rows: list) -> list:
        new_rows = self._payload if isinstance(self._payload, list) else [self._payload]
        added = []
        for new in new_rows:
            row = copy.deepcopy(new)
            if self._table not in _NO_ID_TABLES:
                row.setdefault("id", str(uuid.uuid4()))
                row.setdefault("created_at", datetime.now(UTC).isoformat())
            rows.append(row)
            added.append(copy.deepcopy(row))
        return added


class _FakeRpc:
    def __init__(self, fake: FakeSupabase, name: str, params: dict):
        self._fake, self._name, self._params = fake, name, params

    def execute(self):
        if self._fake.offline:
            raise httpx.ConnectError("Supabase is unreachable (fake)")
        self._fake.calls.append(("rpc", self._name))
        if self._name not in self._fake.rpc_handlers:
            raise NotImplementedError(f"Set fake_supabase.rpc_handlers['{self._name}'] in your test.")
        return SimpleNamespace(data=self._fake.rpc_handlers[self._name](self._params))


class _FakeBucket:
    def __init__(self, fake: FakeSupabase, name: str):
        self._fake, self._name = fake, name

    def upload(self, path, file, file_options=None):
        self._fake.uploads[path] = (file, file_options)
        return SimpleNamespace(path=path)

    def get_public_url(self, path: str) -> str:
        return f"https://fake.supabase.test/storage/v1/object/public/{self._name}/{path}"


class _FakeStorage:
    def __init__(self, fake: FakeSupabase):
        self._fake = fake

    def from_(self, bucket: str) -> _FakeBucket:
        return _FakeBucket(self._fake, bucket)


class _FakeAuth:
    def __init__(self, fake: FakeSupabase):
        self._fake = fake

    def sign_in_with_password(self, credentials: dict):
        email, password = credentials["email"], credentials["password"]
        if self._fake.passwords.get(email) != password:
            # The real Supabase says the same thing for a wrong email or password.
            raise AuthApiError("Invalid login credentials", 400, "invalid_credentials")
        return SimpleNamespace(user=SimpleNamespace(id=self._fake.user_id(email)), session=SimpleNamespace())

    def sign_up(self, credentials: dict):
        email = credentials["email"]
        if email in self._fake.passwords:
            raise AuthApiError("User already registered", 422, "user_already_exists")
        user_id = str(uuid.uuid4())
        name = credentials.get("options", {}).get("data", {}).get("display_name", email)
        self._fake.passwords[email] = credentials["password"]
        # Like the database trigger: every new user is a customer.
        self._fake.tables["profiles"].append(
            {"id": user_id, "email": email, "display_name": name, "role": "customer", "default_address": None})
        session = None if self._fake.confirm_email else SimpleNamespace()
        return SimpleNamespace(user=SimpleNamespace(id=user_id), session=session)

    def reset_password_for_email(self, email, options=None):
        self._fake.reset_emails.append(email)

    def sign_out(self):
        self._fake.signed_out = True


class FakeSupabase:
    """Stands in for supabase.Client in tests."""

    def __init__(self):
        self.tables = sample_tables()
        self.passwords = {row["email"]: FAKE_PASSWORD for row in self.tables["profiles"]}
        self.test_password = FAKE_PASSWORD  # every sample account's password in this fake
        self.rpc_handlers: dict = {}  # name -> function(params) -> data
        self.calls: list[tuple[str, str]] = []  # every (action, table) the app made
        self.uploads: dict = {}
        self.reset_emails: list[str] = []
        self.signed_out = False
        self.offline = False  # True = pretend Supabase can't be reached
        self.confirm_email = False  # True = sign-up waits for email confirmation
        self.auth = _FakeAuth(self)
        self.storage = _FakeStorage(self)

    def user_id(self, email: str) -> str:
        return next(row["id"] for row in self.tables["profiles"] if row["email"] == email)

    def rows(self, table: str) -> list[dict]:
        return self.tables.get(table, [])

    def table(self, name: str) -> _FakeQuery:
        return _FakeQuery(self, name)

    def rpc(self, name: str, params: dict | None = None) -> _FakeRpc:
        return _FakeRpc(self, name, params or {})


def db_error(message: str) -> APIError:
    """The error the real client raises when a database function says no."""
    return APIError({"message": message, "code": "P0001", "hint": None, "details": None})


# --- Fixtures ----------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_session_state():
    """Each test starts with an empty st.session_state (it's shared outside a real app)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    yield
    for key in list(st.session_state.keys()):
        del st.session_state[key]


@pytest.fixture
def fake_supabase(monkeypatch) -> FakeSupabase:
    """Make every service use a fresh FakeSupabase for this test."""
    fake = FakeSupabase()
    for module in ("supabase_client", "auth", "catalog", "cart", "orders", "admin", "profile"):
        target = f"app.services.{module}"
        __import__(target)
        if hasattr(sys.modules[target], "get_client"):
            monkeypatch.setattr(f"{target}.get_client", lambda: fake)
    return fake


def _sign_in_as(user_id: str) -> CurrentUser:
    row = next(row for row in sample_tables()["profiles"] if row["id"] == user_id)
    user = CurrentUser(row["id"], row["email"], row["display_name"], row["role"])
    st.session_state["current_user"] = user
    return user


@pytest.fixture
def as_customer(fake_supabase) -> CurrentUser:
    """The demo customer is signed in (no password step needed)."""
    return _sign_in_as(CUSTOMER_ID)


@pytest.fixture
def as_staff(fake_supabase) -> CurrentUser:
    return _sign_in_as(STAFF_ID)


@pytest.fixture
def as_owner(fake_supabase) -> CurrentUser:
    return _sign_in_as(OWNER_ID)


@pytest.fixture
def sample_chips() -> list[BaseChip]:
    """The 4 active base chips from the seed, as BaseChip objects."""
    from app.services.catalog import _base_chip_from_row

    return [_base_chip_from_row(row) for row in sample_tables()["base_chips"] if row["is_active"]]


@pytest.fixture
def sample_flavors() -> list[Flavor]:
    """The 10 flavors from the seed, as Flavor objects. Truffle Herb is sold out."""
    return [
        Flavor(row["id"], row["name"], row["description"], row["family"], row["salty"], row["tangy"],
               row["sweet"], row["heat"], Decimal(str(row["price"])), row["stock"], tuple(row["allergens"]))
        for row in sample_tables()["flavors"]
    ]
