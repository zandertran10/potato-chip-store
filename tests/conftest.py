"""Shared test setup: a fake Supabase client and sample data.

Unit tests never touch a real Supabase project or real keys. The fake client
answers the same calls the app makes (sign-in, sign-up, sign-out, and simple
table reads), using the sample data below, which matches the demo seed
(supabase/seed/01_catalog.sql and docs/deployment/demo-accounts.md).

How to use it in a test:

    def test_something(fake_supabase):           # the app now talks to the fake
        user = auth.sign_in("customer@demo.test", fake_supabase.test_password)
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

# Let tests `import app...` from the repo root, however pytest is started.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# These imports must stay BELOW the path fix above, or `app` can't be found.
import streamlit as st
from supabase_auth.errors import AuthApiError

from app.models.catalog import BaseChip, Flavor

# Test-only passwords for the FAKE client. They are not the real demo passwords,
# which are never written in the repo (docs/deployment/demo-accounts.md).
FAKE_PASSWORD = "TestOnly123"


# --- Sample data ---------------------------------------------------------------

SAMPLE_PROFILES = {
    "00000000-0000-4000-8000-0000000000a1": {
        "email": "owner@demo.test", "display_name": "Olive Owner", "role": "owner"},
    "00000000-0000-4000-8000-0000000000a2": {
        "email": "staff@demo.test", "display_name": "Sam Staff", "role": "staff"},
    "00000000-0000-4000-8000-0000000000a3": {
        "email": "customer@demo.test", "display_name": "Casey Customer", "role": "customer"},
}


@pytest.fixture
def sample_chips() -> list[BaseChip]:
    """The 4 base chips from the seed. Sweet Potato is low on stock on purpose."""
    return [
        BaseChip("00000000-0000-4000-8000-000000000101", "Classic Thin", "Thin and golden.",
                 "Classic", "Thin", 2, Decimal("2.50"), 100, is_featured=True),
        BaseChip("00000000-0000-4000-8000-000000000102", "Kettle Cooked", "Extra-loud crunch.",
                 "Kettle", "Thick", 3, Decimal("3.00"), 80, is_featured=True),
        BaseChip("00000000-0000-4000-8000-000000000103", "Wavy Ridge", "Holds the seasoning.",
                 "Wavy", "Regular", 2, Decimal("2.75"), 60, is_featured=True),
        BaseChip("00000000-0000-4000-8000-000000000104", "Sweet Potato", "Naturally sweet.",
                 "Sweet potato", "Regular", 1, Decimal("3.25"), 3),
    ]


@pytest.fixture
def sample_flavors() -> list[Flavor]:
    """A few flavors from the seed. Truffle Herb is sold out on purpose."""
    return [
        Flavor("00000000-0000-4000-8000-000000000201", "Sea Salt", "Flaky sea salt.",
               "Salty", 3, 0, 0, 0, Decimal("0.25"), 200),
        Flavor("00000000-0000-4000-8000-000000000203", "Sour Cream & Onion", "Cool and creamy.",
               "Herby", 1, 1, 0, 0, Decimal("0.50"), 150, allergens=("milk",)),
        Flavor("00000000-0000-4000-8000-000000000204", "Smoky BBQ", "Sweet and smoky.",
               "Spicy", 1, 1, 2, 1, Decimal("0.50"), 120, allergens=("soy",)),
        Flavor("00000000-0000-4000-8000-000000000210", "Truffle Herb", "Earthy herbs.",
               "Herby", 1, 0, 0, 0, Decimal("0.90"), 0, allergens=("milk",)),
    ]


# --- The fake Supabase client --------------------------------------------------

class _FakeQuery:
    """Answers table("profiles").select(...).eq("id", x).maybe_single().execute()."""

    def __init__(self, rows: dict[str, dict]):
        self._rows = rows
        self._id: str | None = None

    def select(self, *_columns):
        return self

    def eq(self, column: str, value: str):
        if column == "id":
            self._id = value
        return self

    def maybe_single(self):
        return self

    def execute(self):
        row = self._rows.get(self._id)
        # Like the real client: None when there's no row.
        return SimpleNamespace(data=dict(row)) if row else None


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
        user_id = f"00000000-0000-4000-8000-{len(self._fake.profiles) + 1:012d}"
        name = credentials.get("options", {}).get("data", {}).get("display_name", email)
        self._fake.passwords[email] = credentials["password"]
        # Like the database trigger: every new user is a customer.
        self._fake.profiles[user_id] = {"email": email, "display_name": name, "role": "customer"}
        return SimpleNamespace(user=SimpleNamespace(id=user_id), session=SimpleNamespace())

    def sign_out(self):
        self._fake.signed_out = True


class FakeSupabase:
    """Stands in for supabase.Client in tests."""

    def __init__(self):
        self.profiles = {key: dict(value) for key, value in SAMPLE_PROFILES.items()}
        self.passwords = {row["email"]: FAKE_PASSWORD for row in self.profiles.values()}
        self.signed_out = False
        # The password every sample account has in this fake.
        self.test_password = FAKE_PASSWORD
        self.auth = _FakeAuth(self)

    def user_id(self, email: str) -> str:
        return next(uid for uid, row in self.profiles.items() if row["email"] == email)

    def table(self, name: str) -> _FakeQuery:
        if name != "profiles":
            raise NotImplementedError(f"The fake client has no '{name}' table yet; add it here.")
        return _FakeQuery(self.profiles)


# --- Fixtures ------------------------------------------------------------------

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
    """Make the app's services use a fresh FakeSupabase for this test."""
    fake = FakeSupabase()
    monkeypatch.setattr("app.services.supabase_client.get_client", lambda: fake)
    monkeypatch.setattr("app.services.auth.get_client", lambda: fake)
    return fake
