"""
EzraApiClient
=============
Thin, authenticated HTTP client for the Ezra staging API.

All base URLs, client IDs, and timeouts are read from environment variables
so the same client works against any environment (staging, prod) without
code changes.

Environment variables
---------------------
EZRA_BASE_URL   Base URL of the API  (default: https://stage-api.ezra.com)
EZRA_CLIENT_ID  OAuth2 client ID     (default: F59A84B4-…)
EZRA_TIMEOUT    Request timeout in s (default: 30)
EZRA_ORIGIN     Browser-origin header for CORS (default: https://myezra-staging.ezra.com)
EZRA_REFERER    Referer header       (default: <ORIGIN>/)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

# ── Configuration (all overridable via environment) ─────────────────────────
BASE_URL  = os.getenv("EZRA_BASE_URL",   "https://stage-api.ezra.com").rstrip("/")
CLIENT_ID = os.getenv("EZRA_CLIENT_ID",  "F59A84B4-6E6B-4678-97A0-11C0F6E0719F")
TIMEOUT   = float(os.getenv("EZRA_TIMEOUT", "30"))
ORIGIN    = os.getenv("EZRA_ORIGIN",  "https://myezra-staging.ezra.com")
REFERER   = os.getenv("EZRA_REFERER", f"{ORIGIN}/")


@dataclass
class ApiUser:
    """Holds credentials and the questionnaire submission ID for a single test user.

    All values are loaded from fixtures/test_users.json — nothing is hardcoded
    and no environment variables are required.

    Attributes:
        username:     Email address used for OAuth2 login.
        password:     Account password.
        submission_id: Numeric ID of the medical-questionnaire submission
                       (stored as a string, e.g. "3521").
    """
    username:      str
    password:      str
    submission_id: str


class EzraApiClient:
    """Authenticated HTTP client for the Ezra staging REST API.

    Usage::

        client = EzraApiClient(username="user@example.com", password="secret")
        client.authenticate()          # obtains + stores Bearer token
        client.get_current_member()    # stores member_id for subsequent calls
        resp = client.get_submission_detail(submission_id)
    """

    def __init__(self, username: str, password: str) -> None:
        self.username  = username
        self.password  = password
        self.member_id: Optional[str] = None

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept":     "application/json, text/plain, */*",
                "Origin":     ORIGIN,
                "Referer":    REFERER,
                "User-Agent": "Mozilla/5.0 Ezra QA API Tests",
            }
        )

    # ── Internal helpers ────────────────────────────────────────────────────

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send a request to BASE_URL + path."""
        return self.session.request(
            method, f"{BASE_URL}{path}", timeout=TIMEOUT, **kwargs
        )

    # ── Authentication ───────────────────────────────────────────────────────

    def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Ezra identity server using the resource-owner
        password grant and store the resulting Bearer token in the session.

        Returns:
            Full token response payload (access_token, refresh_token, …).

        Raises:
            requests.HTTPError: If authentication fails (4xx / 5xx).
        """
        response = self._request(
            "POST",
            "/individuals/member/connect/token",
            headers={
                "Accept":       "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "password",
                "scope":      "openid offline_access profile roles email",
                "username":   self.username,
                "password":   self.password,
                "client_id":  CLIENT_ID,
            },
        )
        response.raise_for_status()
        payload = response.json()
        self.session.headers["Authorization"] = f"Bearer {payload['access_token']}"
        return payload

    def get_current_member(self) -> Dict[str, Any]:
        """
        Fetch the authenticated member's profile and cache their member ID.

        Returns:
            Member profile payload (id, name, email, …).

        Raises:
            requests.HTTPError: On a non-2xx response.
        """
        response = self._request("GET", "/individuals/api/members")
        response.raise_for_status()
        payload = response.json()
        self.member_id = payload["id"]
        return payload

    # ── Encounter / booking lookup ───────────────────────────────────────────

    def get_encounters(self) -> requests.Response:
        """
        Fetch all booking encounters for the authenticated member.

        Returns:
            Raw :class:`requests.Response` containing a list of encounter objects.
            Each encounter has at least an ``id`` (UUID) and ``createdOn`` field.
        """
        assert self.member_id, "Call get_current_member() before get_encounters()."
        return self._request(
            "GET",
            f"/scheduling/api/appointments/member/{self.member_id}",
        )

    def get_latest_encounter_id(self) -> Optional[str]:
        """
        Automatically fetch and return the most recently created encounter ID
        for this member — no env var or manual lookup required.

        Tries two common endpoint patterns; returns None if neither works or
        the member has no bookings yet.

        Returns:
            encounter_id string (UUID), or None if not found.
        """
        assert self.member_id, "Call get_current_member() before get_latest_encounter_id()."

        # Try scheduling endpoint first
        endpoints = [
            f"/scheduling/api/appointments/member/{self.member_id}",
            f"/platform/api/members/{self.member_id}/encounters",
            f"/packages/api/payments/member/{self.member_id}",
        ]

        for path in endpoints:
            try:
                resp = self._request("GET", path)
                if resp.status_code == 200:
                    data = resp.json()
                    # Handle both list and {"items": [...]} shapes
                    items = data if isinstance(data, list) else data.get("items", data.get("encounters", data.get("appointments", [])))
                    if items:
                        # Sort by createdOn descending and return most recent id
                        sorted_items = sorted(
                            items,
                            key=lambda x: x.get("createdOn", x.get("appointmentDate", "")),
                            reverse=True,
                        )
                        encounter = sorted_items[0]
                        return (
                            encounter.get("encounterId")
                            or encounter.get("id")
                            or encounter.get("appointmentId")
                        )
            except Exception:
                continue

        return None

    # ── Booking endpoints ────────────────────────────────────────────────────

    def mark_booking_stage(
        self,
        encounter_id: str,
        stage: str = "PAYMENT_PAGE",
    ) -> requests.Response:
        """
        Advance a booking to a given stage (e.g. PAYMENT_PAGE).

        Args:
            encounter_id: UUID of the encounter / appointment.
            stage:        Target stage name (default: ``PAYMENT_PAGE``).

        Returns:
            Raw :class:`requests.Response` (caller asserts status code).
        """
        assert self.member_id, "Call get_current_member() before mark_booking_stage()."
        body = {
            "memberId":   self.member_id,
            "encounterId": encounter_id,
            "stage":      stage,
            "visitedOn":  datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        return self._request("POST", "/platform/api/members/bookingstage", json=body)

    def create_pending_payment(self, encounter_id: str) -> requests.Response:
        """
        Create a pending payment record for an encounter.

        Args:
            encounter_id: UUID of the encounter.

        Returns:
            Raw :class:`requests.Response`.
        """
        body = {
            "creditAppliedCents": 0,
            "paymentPlan":        "oneTime",
            "promotionCode":      "",
            "isDeferred":         False,
        }
        return self._request(
            "POST",
            f"/packages/api/payments/{encounter_id}/create-pending",
            json=body,
        )

    # ── Questionnaire endpoints ──────────────────────────────────────────────

    def start_or_fetch_submission(
        self,
        member_id: str,
        encounter_id: str,
    ) -> requests.Response:
        """
        Start (or retrieve an existing) medical-questionnaire submission for a
        given member + encounter combination.

        Args:
            member_id:    UUID of the member who owns the submission.
            encounter_id: UUID of the encounter.

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "POST",
            f"/diagnostics/api/medicaldata/forms/mq/submissions/{member_id}/{encounter_id}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="",
        )

    def get_submission_detail(self, submission_id: str) -> requests.Response:
        """
        Retrieve the full detail (questions + answers) for a questionnaire submission.

        Args:
            submission_id: UUID of the submission.

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "GET",
            f"/diagnostics/api/medicaldata/forms/mq/submissions/{submission_id}/detail",
        )

    def save_submission_answer(
        self,
        submission_numeric_id: str,
        key: str,
        value: Any,
    ) -> requests.Response:
        """
        Save a single answer to a questionnaire submission.

        Args:
            submission_numeric_id: Integer (as str) ID of the submission.
            key:                   Question key (e.g. ``"medicalHistoryAttestation"``).
            value:                 Answer value (will be JSON-serialised).

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "POST",
            f"/diagnostics/api/medicaldata/forms/mq/submissions/{submission_numeric_id}/data",
            json={
                "key":       key,
                "value":     json.dumps(value),
                "hasAnswer": True,
            },
        )

    def complete_submission(self, submission_numeric_id: str) -> requests.Response:
        """
        Mark a questionnaire submission as complete.

        Args:
            submission_numeric_id: Integer (as str) ID of the submission.

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "POST",
            f"/diagnostics/api/medicaldata/forms/mq/submissions/{submission_numeric_id}/complete",
        )

    def get_requires_async_ic(self, encounter_id: str) -> requests.Response:
        """
        Check whether an encounter requires async informed consent.

        Args:
            encounter_id: UUID of the encounter.

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "GET",
            f"/diagnostics/api/medicaldata/requiresAsyncIc/{encounter_id}",
        )

    def get_report(self, member_id: str, encounter_id: str) -> requests.Response:
        """
        Fetch the Ezra report for a specific member and encounter.

        Args:
            member_id:    UUID of the member.
            encounter_id: UUID of the encounter.

        Returns:
            Raw :class:`requests.Response`.
        """
        return self._request(
            "GET",
            f"/diagnostics/api/report/ezra/{member_id}/{encounter_id}",
        )

