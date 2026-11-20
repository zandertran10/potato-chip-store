"""Audit log (NFR-LOG-02, migration 13): the owner's Activity tab reads it.

The rows themselves are written by database triggers, which unit tests can't
run; these tests cover reading and showing them.
"""

from pathlib import Path

import pytest
from conftest import OWNER_ID
from postgrest.exceptions import APIError
from streamlit.testing.v1 import AppTest

from app.services import admin

ENTRY_POINT = str(Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py")

SAMPLE = [
    {"id": 1, "created_at": "2026-11-19T10:00:00+00:00", "actor_id": OWNER_ID, "actor_name": "Olive Owner",
     "actor_role": "owner", "action": "update", "table_name": "settings", "record_id": "1",
     "summary": "Changed store settings", "changes": {"max_flavors": {"from": 3, "to": 2}}},
    {"id": 2, "created_at": "2026-11-19T11:00:00+00:00", "actor_id": None, "actor_name": "Supabase dashboard",
     "actor_role": None, "action": "update", "table_name": "flavors", "record_id": "x",
     "summary": 'Hid flavor "Truffle Herb"', "changes": {"is_active": {"from": True, "to": False}}},
]


def test_entries_are_newest_first_with_who_and_what(as_owner, fake_supabase):
    fake_supabase.tables["audit_log"] = [dict(row) for row in SAMPLE]

    entries = admin.audit_entries()

    assert [e.summary for e in entries] == ['Hid flavor "Truffle Herb"', "Changed store settings"]
    assert entries[1].actor_name == "Olive Owner" and entries[1].actor_role == "owner"
    assert entries[1].changes == {"max_flavors": {"from": 3, "to": 2}}


@pytest.mark.parametrize("code", ["42P01", "PGRST205"])
def test_a_missing_table_says_it_is_not_set_up(as_owner, monkeypatch, code):
    def no_table(self):
        raise APIError({"message": "relation does not exist", "code": code, "hint": None, "details": None})

    monkeypatch.setattr("conftest._FakeQuery.execute", no_table)

    with pytest.raises(admin.AuditLogMissing):
        admin.audit_entries()


def test_activity_tab_shows_the_entries(as_owner, fake_supabase):
    fake_supabase.tables["audit_log"] = [dict(row) for row in SAMPLE]

    at = AppTest.from_file(ENTRY_POINT, default_timeout=30)
    at.session_state["current_user"] = as_owner
    at.switch_page("pages/admin_dashboard.py").run()

    assert not at.exception, at.exception
    table = at.dataframe[0].value
    assert list(table["What"]) == ['Hid flavor "Truffle Herb"', "Changed store settings"]
    assert "Supabase dashboard" in list(table["Who"])
