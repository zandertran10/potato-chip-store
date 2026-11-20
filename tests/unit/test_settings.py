"""app/config/settings.py: which key names are read, and that secret keys are refused (D4)."""

import base64
import json

import pytest

from app.config import settings

URL = "https://example.supabase.co"


@pytest.fixture
def env(monkeypatch):
    """Control the settings completely: no real .env, no secrets.toml, only what the test sets."""
    monkeypatch.setattr(settings, "load_dotenv", lambda **_: None)
    for name in (settings.URL_SETTING, settings.KEY_SETTING, settings.OLD_KEY_SETTING):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_the_new_key_name_is_read(env):
    env.setenv("SUPABASE_URL", URL)
    env.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_new")

    assert settings.read_settings() == (URL, "sb_publishable_new")


def test_an_old_env_with_supabase_anon_key_still_works(env):
    env.setenv("SUPABASE_URL", URL)
    env.setenv("SUPABASE_ANON_KEY", "sb_publishable_old")

    assert settings.read_settings() == (URL, "sb_publishable_old")


def test_the_new_name_wins_when_both_are_set(env):
    env.setenv("SUPABASE_URL", URL)
    env.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_new")
    env.setenv("SUPABASE_ANON_KEY", "sb_publishable_old")

    assert settings.read_settings()[1] == "sb_publishable_new"


def test_missing_settings_read_as_empty(env):
    assert settings.read_settings() == ("", "")


def _jwt(role: str) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"role": role}).encode()).decode().rstrip("=")
    return f"header.{body}.signature"


@pytest.mark.parametrize(
    ("key", "refused"),
    [
        ("sb_secret_abc123", True),  # new-style secret key
        (_jwt("service_role"), True),  # old-style service_role key
        ("sb_publishable_abc123", False),
        (_jwt("anon"), False),  # old-style anon key
    ],
)
def test_secret_keys_are_refused(key, refused):
    assert settings.is_service_role_key(key) is refused
