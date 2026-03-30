"""
conftest.py — shared pytest fixtures for the Ezra API test suite.

All user data (username, password, submission_id) is loaded directly from
../fixtures/test_users.json — the same file used by the Playwright UI tests.

  member_a  →  users[0]  (first registered user)
  member_b  →  users[1]  (second registered user)

No environment variables are required to run these tests.
"""

import json
from pathlib import Path

import pytest

from client.ezra_api_client import EzraApiClient, ApiUser

_USERS_JSON = Path(__file__).resolve().parent.parent / "fixtures" / "test_users.json"


def _load_users() -> list:
    """Load users from test_users.json and validate at least 2 exist."""
    if not _USERS_JSON.exists():
        raise FileNotFoundError(
            f"test_users.json not found at {_USERS_JSON}. "
            "Run the UI signup test first to populate it."
        )
    with _USERS_JSON.open() as f:
        data = json.load(f)
    users = data.get("users", [])
    if len(users) < 2:
        raise ValueError(
            f"test_users.json must contain at least 2 users "
            f"(found {len(users)}). Run the UI signup test to register more users."
        )
    return users


# ── User data fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def member_a() -> ApiUser:
    """
    First test user — loaded from test_users.json.
    
    Uses the second-to-last user in the list (most recent user with active booking from UI test).
    This ensures API tests run against freshly created accounts with bookings.
    """
    users = _load_users()
    
    # Use second-to-last user (or first if only 1 exists)
    idx = max(0, len(users) - 2)
    user = users[idx]
    
    return ApiUser(
        username=user["email"],
        password=user["password"],
        submission_id=str(user.get("submission_id", "")),
    )


@pytest.fixture(scope="session")
def member_b() -> ApiUser:
    """
    Second test user — loaded from test_users.json.
    
    Uses the last user in the list (most recently created by UI booking test).
    """
    users = _load_users()
    user = users[-1]
    
    return ApiUser(
        username=user["email"],
        password=user["password"],
        submission_id=str(user.get("submission_id", "")),
    )


# ── Authenticated API client fixtures ────────────────────────────────────────

@pytest.fixture()
def member_a_client(member_a: ApiUser) -> EzraApiClient:
    """
    Authenticated EzraApiClient for member A.
    Automatically fetches the latest encounter_id after login —
    no environment variable needed.
    """
    client = EzraApiClient(member_a.username, member_a.password)
    client.authenticate()
    client.get_current_member()
    # Auto-fetch the most recent encounter so tests never need an env var
    client.latest_encounter_id = client.get_latest_encounter_id()
    return client


@pytest.fixture()
def member_b_client(member_b: ApiUser) -> EzraApiClient:
    """
    Authenticated EzraApiClient for member B.
    Automatically fetches the latest encounter_id after login —
    no environment variable needed.
    """
    client = EzraApiClient(member_b.username, member_b.password)
    client.authenticate()
    client.get_current_member()
    client.latest_encounter_id = client.get_latest_encounter_id()
    return client
