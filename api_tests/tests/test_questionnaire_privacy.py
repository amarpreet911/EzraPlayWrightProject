"""
test_questionnaire_privacy.py
=============================
Authorization and data-privacy tests — verifies that one authenticated member
CANNOT access, modify, or complete another member's medical questionnaire.

All test data (username, password, submission_id) is loaded automatically from
fixtures/test_users.json — no environment variables required.

Markers: @pytest.mark.api, @pytest.mark.privacy
"""

import sys
from pathlib import Path

# Ensure api_tests/ is on the path so 'client' resolves both in the IDE and at runtime
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from client.ezra_api_client import EzraApiClient, ApiUser


@pytest.mark.api
@pytest.mark.privacy
class TestQuestionnairePrivacyAuthorization:
    """
    Member A's authenticated session must NOT be able to read, write, or
    complete Member B's medical questionnaire.

    PASS = API returns 401 / 403 / 404  (request correctly blocked)
    FAIL = API returns 2xx              (security violation — cross-member access allowed)
    """

    def test_member_cannot_read_another_members_questionnaire_detail(
        self,
        member_a_client: EzraApiClient,
        member_b: ApiUser,
    ) -> None:
        """
        GET .../mq/submissions/{member_b.submission_id}/detail

        Member A tries to read Member B's questionnaire answers.
        Expected: 401 / 403 / 404 / 405 (blocked)
        """
        response = member_a_client.get_submission_detail(member_b.submission_id)

        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: Member A read Member B's questionnaire detail. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

    def test_member_cannot_update_another_members_questionnaire_answers(
        self,
        member_a_client: EzraApiClient,
        member_b: ApiUser,
    ) -> None:
        """
        POST .../mq/submissions/{member_b.submission_id}/data

        Member A tries to write an answer into Member B's questionnaire.
        Expected: 401 / 403 / 404 / 405 (blocked)
        """
        response = member_a_client.save_submission_answer(
            submission_numeric_id=member_b.submission_id,
            key="medicalHistoryAttestation",
            value="yes",
        )

        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: Member A updated Member B's questionnaire answer. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

    def test_member_cannot_complete_another_members_questionnaire(
        self,
        member_a_client: EzraApiClient,
        member_b: ApiUser,
    ) -> None:
        """
        POST .../mq/submissions/{member_b.submission_id}/complete

        Member A tries to mark Member B's questionnaire as complete.
        Expected: 401 / 403 / 404 / 405 (blocked)
        """
        response = member_a_client.complete_submission(member_b.submission_id)

        assert response.status_code in (401, 403, 404, 405), (
            f"SECURITY VIOLATION: Member A completed Member B's questionnaire. "
            f"Expected 401/403/404/405, got {response.status_code}: {response.text}"
        )

