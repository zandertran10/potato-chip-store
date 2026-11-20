"""App settings: where the Supabase project is and which key to use.

Values come from `.streamlit/secrets.toml` (used on Streamlit Community Cloud)
or, if not there, from `.env` / environment variables (handy on a laptop).
Both files are gitignored, so keys never end up in GitHub (NFR-SEC-09).

The key is Supabase's PUBLISHABLE key (sb_publishable_..., formerly "anon").
Its setting is SUPABASE_PUBLISHABLE_KEY; the older name SUPABASE_ANON_KEY is
still accepted, so existing .env files keep working (decisions.md, D4).
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

URL_SETTING = "SUPABASE_URL"
KEY_SETTING = "SUPABASE_PUBLISHABLE_KEY"
OLD_KEY_SETTING = "SUPABASE_ANON_KEY"  # still accepted


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_publishable_key: str


def _read_setting(name: str) -> str:
    """Return one setting from st.secrets, then from the environment, or ""."""
    try:
        value = st.secrets.get(name, "")
    except StreamlitSecretNotFoundError:
        # No secrets.toml at all is normal on a laptop that uses .env instead.
        value = ""
    return str(value or os.getenv(name, "")).strip()


def is_service_role_key(key: str) -> bool:
    """True if `key` is a secret (formerly service-role) key, which must never be in the app.

    Those keys skip every security rule in the database (NFR-SEC-10).
    New-style secret keys start with "sb_secret_". Old-style keys are JWTs whose
    middle part says {"role": "service_role"}.
    """
    if key.startswith("sb_secret_"):
        return True
    parts = key.split(".")
    if len(parts) != 3:
        return False
    try:
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
    except (ValueError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and payload.get("role") == "service_role"


def read_settings() -> tuple[str, str]:
    """The URL and key as configured ("" when missing). The new key name wins over the old one."""
    # Reads .env into the environment. Existing environment variables win.
    load_dotenv(override=False)
    return _read_setting(URL_SETTING), _read_setting(KEY_SETTING) or _read_setting(OLD_KEY_SETTING)


def get_settings() -> Settings:
    """Load the settings, or stop the page with a clear message if they're wrong."""
    url, key = read_settings()

    missing = [name for name, value in ((URL_SETTING, url), (KEY_SETTING, key)) if not value]
    if missing:
        st.error(
            f"The store isn't set up yet: {', '.join(missing)} is missing. "
            "Copy `.env.example` to `.env` (or `.streamlit/secrets.toml.example` "
            "to `.streamlit/secrets.toml`) and fill in your Supabase project URL "
            "and publishable key.",
            icon=":material/settings:",
        )
        st.stop()

    if is_service_role_key(key):
        st.error(
            "The Supabase key is a SECRET key (sb_secret_..., formerly service_role). "
            "That key skips every security rule, so the app refuses to use it. "
            "Use the publishable key (sb_publishable_...) instead.",
            icon=":material/gpp_bad:",
        )
        st.stop()

    return Settings(supabase_url=url, supabase_publishable_key=key)
