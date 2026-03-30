"""
test_e2e_booking_and_privacy.py
===============================
Complete end-to-end test combining booking flow happy-path and privacy checks.

This test:
  1. Tests User A's full booking + questionnaire flow (happy path)
  2. Dynamically captures submission_id from API response
  3. Tests User A trying to access User B's questionnaire (security checks)
  4. Uses shared fixtures for both E2E and privacy validation

Markers: @pytest.mark.api, @pytest.mark.e2e

No environment variables required — all data loaded from fixtures/test_users.json
and auto-fetched from the API (encounter_id, member_id, submission_id).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from client.ezra_api_client import EzraApiClient, ApiUser


import os

def _require_encounter(client: EzraApiClient) -> str:
    """
    Return encounter_id with priority:
    1. Check EZRA_ENCOUNTER_ID env var (fastest, for CI/fast runs)
    2. Try to auto-fetch from API (for normal runs)
    3. Skip gracefully if not found (expected for new users)
    
    Returns:
        encounter_id (UUID string)
    
    Raises:
        pytest.skip if no encounter found via either method
    """
    # Priority 1: Environment variable (allows skipping API call in CI)
    eid = os.getenv("EZRA_ENCOUNTER_ID")
    if eid:
        return eid
    
    # Priority 2: Auto-fetch from API
    eid = getattr(client, "latest_encounter_id", None)
    if eid:
        return eid
    
    # Fallback: No encounter found - skip gracefully
    pytest.skip(
        "No encounter_id found:\n"
        "  • ENV VAR: EZRA_ENCOUNTER_ID not set\n"
        "  • AUTO-FETCH: No bookings found via API\n"
        "  → Run UI booking test first: pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s\n"
        "  → Or set env var: export EZRA_ENCOUNTER_ID='your-uuid-here'"
    )


@pytest.mark.api
@pytest.mark.e2e
class TestCompleteE2EBookingAndPrivacyFlow:
    """
    End-to-end test combining booking flow happy-path and privacy/security checks.
    
    Uses:
    - member_a / member_a_client  → User A (acting member)
    - member_b / member_b_client  → User B (privacy target)
    
    Flow:
    1. User A advances their booking to PAYMENT_PAGE
    2. User A creates pending payment for their booking
    3. User A starts/fetches their questionnaire (captures submission_id from response)
    4. User A reads their own questionnaire detail
    5. User A saves an answer to their questionnaire
    6. User A completes their questionnaire
    7. User A tries to read User B's questionnaire → BLOCKED (security)
    8. User A tries to write User B's questionnaire → BLOCKED (security)
    9. User A tries to complete User B's questionnaire → BLOCKED (security)
    """

    # ── PART 1: User A's Booking Happy Path ────────────────────────────────

    def test_e2e_1_user_a_advances_booking_to_payment_stage(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """User A advances their booking to PAYMENT_PAGE stage."""
        encounter_id = _require_encounter(member_a_client)
        response = member_a_client.mark_booking_stage(encounter_id, stage="PAYMENT_PAGE")
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )

    def test_e2e_2_user_a_creates_pending_payment(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """User A creates a pending payment for their booking."""
        encounter_id = _require_encounter(member_a_client)
        response = member_a_client.create_pending_payment(encounter_id)
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )

    def test_e2e_3_user_a_starts_questionnaire(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """
        User A starts/fetches their questionnaire for their booking.
        Captures submission_id from the response for use in subsequent tests.
        """
        encounter_id = _require_encounter(member_a_client)
        response = member_a_client.start_or_fetch_submission(
            member_id=member_a_client.member_id,
            encounter_id=encounter_id,
        )
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )
        
        # Capture submission_id from response for use in later tests
        payload = response.json()
        submission_id = payload.get("id")
        assert submission_id, "No submission ID in response"
        
        # Store on the client object for other tests to access
        member_a_client.submission_id = submission_id

    def test_e2e_4_user_a_reads_own_questionnaire(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """User A reads the detail of their own questionnaire."""
        # Use the submission_id captured in test 3
        submission_id = getattr(member_a_client, "submission_id", None)
        if not submission_id:
            pytest.skip(
                "No submission_id captured from start_questionnaire step. "
                "Run test_e2e_3 first."
            )
        
        response = member_a_client.get_submission_detail(submission_id)
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )

    def test_e2e_5_user_a_saves_questionnaire_answer(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """User A saves an answer to their questionnaire."""
        submission_id = getattr(member_a_client, "submission_id", None)
        if not submission_id:
            pytest.skip("No submission_id available")
        
        response = member_a_client.save_submission_answer(
            submission_numeric_id=submission_id,
            key="medicalHistoryAttestation",
            value="yes",
        )
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )

    def test_e2e_6_user_a_completes_questionnaire(
        self,
        member_a_client: EzraApiClient,
    ) -> None:
        """User A completes their questionnaire."""
        submission_id = getattr(member_a_client, "submission_id", None)
        if not submission_id:
            pytest.skip("No submission_id available")
        
        response = member_a_client.complete_submission(submission_id)
        assert response.status_code < 400, (
            f"Expected 2xx, got {response.status_code}: {response.text}"
        )

    # ── PART 2: Security Checks — User A tries to access User B's data ──────

    def test_e2e_7_user_a_cannot_read_user_b_questionnaire(
        self,
        member_a_client: EzraApiClient,
        member_b_client: EzraApiClient,
    ) -> None:
        """
        SECURITY: User A tries to read User B's questionnaire — should be blocked.
        Dynamically fetches User B's submission_id from the API.
        """
        # Fetch User B's submission_id from their API (if it exists)
        b_submission_id = getattr(member_b_client, "submission_id", None)
        
        # If not cached, try to create one by starting a questionnaire
        if not b_submission_id:
            # User B may have an encounter — try to fetch/create submission
            encounter_id = getattr(member_b_client, "latest_encounter_id", None)
            if encounter_id:
                resp = member_b_client.start_or_fetch_submission(
                    member_id=member_b_client.member_id,
                    encounter_id=encounter_id,
                )
                if resp.status_code == 200:
                    payload = resp.json()
                    b_submission_id = payload.get("id")
        
        if not b_submission_id:
            pytest.skip(
                "Cannot determine User B's submission_id. "
                "User B may not have any bookings/questionnaires yet."
            )
        
        # Now attempt cross-member access with User A's client
        response = member_a_client.get_submission_detail(b_submission_id)

        # 401/403/404/405 all indicate the request was blocked (success)
        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: User A read User B's questionnaire. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

    def test_e2e_8_user_a_cannot_write_user_b_questionnaire(
        self,
        member_a_client: EzraApiClient,
        member_b_client: EzraApiClient,
    ) -> None:
        """SECURITY: User A tries to write User B's questionnaire — should be blocked."""
        b_submission_id = getattr(member_b_client, "submission_id", None)
        
        if not b_submission_id:
            encounter_id = getattr(member_b_client, "latest_encounter_id", None)
            if encounter_id:
                resp = member_b_client.start_or_fetch_submission(
                    member_id=member_b_client.member_id,
                    encounter_id=encounter_id,
                )
                if resp.status_code == 200:
                    payload = resp.json()
                    b_submission_id = payload.get("id")
        
        if not b_submission_id:
            pytest.skip("Cannot determine User B's submission_id")
        
        response = member_a_client.save_submission_answer(
            submission_numeric_id=b_submission_id,
            key="medicalHistoryAttestation",
            value="yes",
        )

        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: User A wrote User B's questionnaire. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

    def test_e2e_9_user_a_cannot_complete_user_b_questionnaire(
        self,
        member_a_client: EzraApiClient,
        member_b_client: EzraApiClient,
    ) -> None:
        """SECURITY: User A tries to complete User B's questionnaire — should be blocked."""
        b_submission_id = getattr(member_b_client, "submission_id", None)
        
        if not b_submission_id:
            encounter_id = getattr(member_b_client, "latest_encounter_id", None)
            if encounter_id:
                resp = member_b_client.start_or_fetch_submission(
                    member_id=member_b_client.member_id,
                    encounter_id=encounter_id,
                )
                if resp.status_code == 200:
                    payload = resp.json()
                    b_submission_id = payload.get("id")
        
        if not b_submission_id:
            pytest.skip("Cannot determine User B's submission_id")
        
        response = member_a_client.complete_submission(b_submission_id)

        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: User A completed User B's questionnaire. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

