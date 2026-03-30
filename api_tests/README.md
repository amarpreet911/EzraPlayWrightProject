# Ezra API Test Suite

Pure **HTTP / REST API** tests for the Ezra staging backend — no browser, no
Playwright. Tests run directly against the staging API using authenticated
`requests` sessions and are completely independent of the Playwright UI test suite.

---

## Index

1. [Purpose](#1-purpose)
2. [Package Structure](#2-package-structure)
3. [Where User Data Comes From](#3-where-user-data-comes-from)
4. [What is an Encounter ID?](#4-what-is-an-encounter-id)
5. [Setup](#5-setup)
6. [How to Run](#6-how-to-run)
   - 6.1 [First — cd into the right directory](#61-first--cd-into-the-right-directory)
   - 6.2 [Run ALL API tests](#62-run-all-api-tests)
   - 6.3 [Run booking flow tests only](#63-run-booking-flow-tests-only)
   - 6.4 [Run privacy / security tests only](#64-run-privacy--security-tests-only)
   - 6.5 [Run a single test](#65-run-a-single-test)
   - 6.6 [Run the E2E story script](#66-run-the-e2e-story-script)
   - 6.7 [Run by marker](#67-run-by-marker)
   - 6.8 [Run with HTML report](#68-run-with-html-report)
   - 6.9 [Quick-reference cheat sheet](#69-quick-reference-cheat-sheet)
7. [How It Works](#7-how-it-works)
8. [Relationship to the Playwright UI Suite](#8-relationship-to-the-playwright-ui-suite)

---

## 1. Purpose

| File | Tests | What it tests |
|---|---|---|
| `tests/test_questionnaire_privacy.py` | 3 | **Security**: a member cannot read, write, or complete another member's questionnaire. **Always passing ✅** |
| `tests/test_e2e_booking_and_privacy.py` | 9 | **Complete E2E flow**: booking progression (6 tests) + privacy checks (3 tests) combined into one narrative |

**Total: 12 tests** (3 passing + 9 skippable based on data availability)

The privacy tests directly verify the API-layer aspect of **BUG-03** (identity
isolation — see `../BUG_REPORT.md`). A `2xx` response from any privacy test is
a **security violation** — the test will fail and flag it immediately.


---

## 2. Package Structure

```
api_tests/
├── __init__.py
├── requirements.txt          ← Python deps (requests, pytest)
├── pytest.ini                ← pytest config for this package
├── conftest.py               ← shared fixtures (auto-authenticated API clients)
├── client/
│   ├── __init__.py
│   └── ezra_api_client.py    ← EzraApiClient + ApiUser dataclass
└── tests/
    ├── __init__.py
    ├── test_questionnaire_privacy.py   ← 3 security tests (always passing ✅)
    └── test_e2e_booking_and_privacy.py ← 9 E2E tests (booking + privacy combined)
```

---

## 3. Where User Data Comes From

**Everything is automatic — no environment variables required.**

| Data | Source | How |
|---|---|---|
| `username` / `password` | `../fixtures/test_users.json` | Loads `users[0]` and `users[1]` automatically |
| `encounter_id` | **API — fetched automatically after login** | `get_latest_encounter_id()` queries the API for member's most recent booking |
| `submission_id` | **API — captured dynamically during test execution** | Tests capture from `/start_questionnaire` response, no pre-stored needed |

**Example from `test_users.json`:**

```json
{
  "id": 3,
  "first_name": "Preet3",
  "last_name": "Test3",
  "email": "amarpreet911+3@gmail.com",           ← credentials used for login
  "phone": "1111111111",
  "password": "TestPreet@4263",                  ← credentials used for login
  "created_at": "2026-03-29T10:35:36.934191Z"
  // NO submission_id needed — tests capture it from API response
}
```

The API tests automatically:
1. Load credentials from `users[0]` and `users[1]`
2. Authenticate with the API
3. Fetch encounter_id from the API
4. Capture submission_id from the questionnaire start response
5. Run all subsequent tests using the captured IDs

---

## 4. What is an Encounter ID?

An **encounter** is one specific booked scan appointment. Every time a user books
a scan, the backend creates an encounter record with a UUID — the **encounter ID**.

```
User books MRI Scan at New York  →  Backend creates encounter
                                     encounter_id = "abc123-def456-..."
                                     Links: user + scan type + location + date/time + payment
```

### How encounter_id is fetched automatically

After login, `get_latest_encounter_id()` queries the API for all of the member's
bookings, sorts them by date descending, and returns the most recent one:

```
client.authenticate()
client.get_current_member()          → stores member_id
client.get_latest_encounter_id()     → GET /scheduling/api/appointments/member/{id}
                                       → returns most recent encounter UUID
```

**No env var, no copy-paste, no DevTools needed.**

### Why some tests still need it (and what happens without bookings)

Three endpoints are encounter-scoped (they act on one specific booking):

| Test | Endpoint | Why encounter_id is needed |
|---|---|---|
| `test_member_can_advance_booking_to_payment_stage` | `POST /bookingstage` | Must specify which booking to advance |
| `test_member_can_create_pending_payment` | `POST /payments/{encounter_id}/create-pending` | Payment belongs to one booking, not the user |
| `test_member_can_start_own_questionnaire_submission` | `POST /submissions/{member_id}/{encounter_id}` | Questionnaire is linked to one scan appointment |
| `test_member_can_read_own_questionnaire_detail` | `GET /submissions/{submission_id}/detail` | ✅ No encounter needed — always runs |

If the member has **no bookings yet**, the first three tests auto-skip with:
```
SKIPPED: No encounter found for this member.
         Run the UI booking test first to create one:
         pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s
```

### How to get an encounter_id manually (if auto-fetch fails)

**Option A — booking confirmation URL:**
```
https://myezra-staging.ezra.com/book-scan/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                                           ↑ encounter_id
```
**Option B — DevTools:**
Network tab → `/bookingstage` request body → copy `encounterId`

**Option C — override env var** (bypasses auto-fetch):
```bash
export EZRA_USER1_ENCOUNTER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

---

## 5. Setup

### Install dependencies

```bash
pip install -r api_tests/requirements.txt
```

### Ensure test_users.json has at least 2 users

The API tests automatically load credentials from the first two users:

```json
{
  "users": [
    {
      "id": 2,
      "first_name": "Robert",
      "last_name": "blum",
      "email": "amarpreet911+1@gmail.com",
      "password": "Test921@192",
      "phone": "1111111111"
    },
    {
      "id": 3,
      "first_name": "Preet3",
      "last_name": "Test3",
      "email": "amarpreet911+3@gmail.com",
      "password": "TestPreet@4263",
      "phone": "1111111111"
    }
  ]
}
```

**You don't need to add submission_ids** — the tests capture them dynamically from API responses.

If you need more users for future tests, run the UI signup test:
```bash
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s
```

### Optional environment variable overrides

| Variable | Default | Purpose |
|---|---|---|
| `EZRA_BASE_URL` | `https://stage-api.ezra.com` | Point at a different environment |
| `EZRA_CLIENT_ID` | `F59A84B4-...` | OAuth2 client ID |
| `EZRA_TIMEOUT` | `30` | Request timeout in seconds |
| `EZRA_ORIGIN` | `https://myezra-staging.ezra.com` | Origin header |

---

## 6. How to Run

---

### Why Do 9 E2E Tests Skip?

The E2E tests (tests 1-9 in `test_e2e_booking_and_privacy.py`) skip when:
- **No `encounter_id`** — Tests 1-3 need this to advance bookings
- **No `submission_id`** — Tests 4-9 need this to interact with questionnaires

This is **expected and correct behavior** — tests skip gracefully instead of failing.

### How to Make E2E Tests Pass — 3 Approaches

#### **Approach 1: Auto-Fetch from API** (Default, Recommended)
The tests automatically try to fetch encounter_id from the API. This works when:
- User has completed a booking via the UI test
- API endpoints are properly configured

```bash
# 1. Create a booking (generates encounter_id on backend)
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s

# 2. Run API tests (they auto-fetch the encounter_id)
cd api_tests
pytest tests/test_e2e_booking_and_privacy.py -v
```

**Pros:** Zero setup, works automatically
**Cons:** Depends on API endpoint availability

---

#### **Approach 2: Set Environment Variables** (For CI/Fast Runs)
Provide `encounter_id` via env var to skip the API call:

```bash
# Set the encounter_id directly
export EZRA_ENCOUNTER_ID="your-uuid-here"

# Tests use this immediately, no API call needed
pytest tests/test_e2e_booking_and_privacy.py -v
```

Find the encounter_id from:
- Booking confirmation page URL: `https://myezra-staging.ezra.com/sign-up/scan-confirm?encounter=<uuid>`
- Browser DevTools → Network → `/bookingstage` response → copy `encounterId`
- UI test logs at the end

**Pros:** Fast (skips API call), works in CI without browsers
**Cons:** Need to manually find and set the ID

---

#### **Approach 3: Hybrid** (What We Implemented) ✅
Try env var first → fall back to auto-fetch → skip gracefully

```bash
# Option A: Let auto-fetch work (easiest)
pytest tests/test_e2e_booking_and_privacy.py -v

# Option B: Speed it up with env var (no API call)
export EZRA_ENCOUNTER_ID="uuid-here"
pytest tests/test_e2e_booking_and_privacy.py -v

# Option C: Both fail? Skip gracefully with helpful message
pytest tests/test_e2e_booking_and_privacy.py -v
# → SKIPPED: No encounter_id found
#   • ENV VAR: EZRA_ENCOUNTER_ID not set
#   • AUTO-FETCH: No bookings found via API
```

**Pros:** Maximum flexibility, zero required setup, can optimize with env vars
**Cons:** None (this is the best approach)

---

### Why Hybrid Approach is Best:

| Scenario | Hybrid Approach | Auto-Fetch Only | Env Var Only |
|----------|---|---|---|
| **Local dev** | ✅ Works (auto-fetch) | ✅ Works | ❌ Need to find UUID |
| **CI pipeline** | ✅ Works (use env var) | ⚠️ Slow (API call) | ❌ Manual setup |
| **Staging** | ✅ Works (flexible) | ✅ Works | ❌ Manual per run |
| **No bookings** | ✅ Skip gracefully | ✅ Skip gracefully | ✅ Skip gracefully |

---



### 6.1 First — cd into the right directory

All commands below assume you are inside `api_tests/`. Run this once in your
terminal before anything else:

```bash
cd /Users/amarpreetsingh/IdeaProjects/Playwrite_project/api_tests
```

> **No environment variables are required.** Credentials and submission IDs are
> loaded from `fixtures/test_users.json` automatically. Encounter IDs are fetched
> from the API after login.

---

### 6.2 Run ALL API tests

Runs all **12 tests** across both test files:

```bash
pytest tests/ -v -s
```

**Expected output** (with bookings created):

```
tests/test_questionnaire_privacy.py                3 passed
tests/test_e2e_booking_and_privacy.py              9 passed

12 passed in ~5s
```

**Expected output** (without bookings yet):

```
tests/test_questionnaire_privacy.py::...  3 PASSED  ✅ (always works)
tests/test_e2e_booking_and_privacy.py::...  9 SKIPPED (no encounters yet)

3 passed, 9 skipped in ~20s
```

**The structure is clean:**
- `test_questionnaire_privacy.py` — 3 security tests, **always passing** ✅
- `test_e2e_booking_and_privacy.py` — 9 E2E tests, skip gracefully if no bookings

The E2E tests are **smart** — they:
1. Skip gracefully if no encounters exist (no failures)
2. Automatically capture submission_id from API response
3. Use the captured ID for all subsequent steps
4. Test booking flow (6 tests) + security (3 tests) in one narrative

To get full results with bookings:
```bash
cd ..
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s  # Create booking
cd api_tests
pytest tests/ -v -s  # Now 12 passed (E2E tests will run instead of skip)
```

---

### 6.3 Run booking flow tests only (part of E2E)

The booking flow tests are now integrated into the E2E test. Run the first 6 tests:

```bash
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_1_user_a_advances_booking_to_payment_stage -v
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_2_user_a_creates_pending_payment -v
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_3_user_a_starts_questionnaire -v
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_4_user_a_reads_own_questionnaire -v
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_5_user_a_saves_questionnaire_answer -v
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_6_user_a_completes_questionnaire -v
```

Or by marker:

```bash
pytest tests/ -m e2e -v
```

---

### 6.4 Run privacy / security tests only

Tests that member A **cannot** access member B's medical questionnaire:

```bash
pytest tests/test_questionnaire_privacy.py -v
```

Or by marker:

```bash
pytest tests/ -m privacy -v
```

**3 security tests** (all passing ✅):

| # | Test | What it verifies |
|---|---|---|
| 1 | `test_member_cannot_read_another_members_questionnaire_detail` | GET blocked with 401/403/404 |
| 2 | `test_member_cannot_update_another_members_questionnaire_answers` | POST blocked with 401/403/404 |
| 3 | `test_member_cannot_complete_another_members_questionnaire` | POST blocked with 401/403/404 |

> ⚠️ If any of these return `2xx` the test **fails** — that is a security violation.

---

### 6.5 Run a single test

Copy any test's full path and class/method name:

```bash
# Always-runs questionnaire detail test
pytest tests/test_booking_api_flow.py::TestBookingAndQuestionnaireApiFlow::test_member_can_read_own_questionnaire_detail -v -s

# Single privacy test
pytest tests/test_questionnaire_privacy.py::TestQuestionnairePrivacyAuthorization::test_member_cannot_read_another_members_questionnaire_detail -v -s
```

---

### 6.6 Run the E2E story script

The story script runs **all steps in sequence** (booking + questionnaire +
privacy checks) and prints every request URL, status code, and response body
to the console. Best used for exploratory debugging or a quick manual sanity check.

```bash
python scripts/ezra_api_e2e_story.py
```

**What it does:**

```
▶  Authenticating users...
   User 1: amarpreet911+1@gmail.com  |  member_id=...
   User 2: amarpreet911+3@gmail.com  |  member_id=...

▶  Fetching latest encounter IDs automatically...
   User 1 encounter_id: abc123-...
   User 2 encounter_id: def456-...

PART 1 — E2E BOOKING FLOW (User 1 — happy path)
  ✅  Advance booking to PAYMENT_PAGE — OK (200)
  ✅  Create pending payment — OK (200)
  ✅  Start questionnaire submission — OK (200)

PART 2 — QUESTIONNAIRE FLOW (User 1)
  ✅  Read own questionnaire detail — OK (200)
  ✅  Save questionnaire answer — OK (200)
  ✅  Complete questionnaire — OK (200)

PART 3 — PRIVACY / SECURITY CHECKS (User 1 → User 2 resources)
  🔒  User 1 reading User 2's questionnaire detail — correctly blocked (403)
  🔒  User 1 writing User 2's questionnaire answer — correctly blocked (403)
  🔒  User 1 completing User 2's questionnaire — correctly blocked (403)

✅  ALL CHECKS PASSED
```

---

### 6.7 Run by marker

Filter tests by their pytest marker without specifying file names:

```bash
pytest tests/ -m api -v -s           # all API tests (both files)
pytest tests/ -m booking_api -v -s   # booking flow tests only
pytest tests/ -m privacy -v -s       # privacy/security tests only
```

---

### 6.8 Run with HTML report

Generates a self-contained `api_test_report.html` file you can open in a browser:

```bash
pytest tests/ -v -s --html=api_test_report.html --self-contained-html
```

Open the report:
```bash
open api_test_report.html   # macOS
```

---

### 6.9 Quick-reference cheat sheet

```bash
# ── Navigate first ────────────────────────────────────────────────────────
cd /Users/amarpreetsingh/IdeaProjects/Playwrite_project/api_tests

# ── Run everything (auto-fetch encounter_id from API) ────────────────────
pytest tests/ -v                                  # all 12 tests

# ── Run with env var override (skip API call, faster) ──────────────────
export EZRA_ENCOUNTER_ID="your-uuid-here"        # set once
pytest tests/ -v                                  # uses env var, no API call

# ── Run by file ───────────────────────────────────────────────────────────
pytest tests/test_questionnaire_privacy.py -v     # privacy/security (3 tests)
pytest tests/test_e2e_booking_and_privacy.py -v   # E2E booking + privacy (9 tests)

# ── Run by marker ─────────────────────────────────────────────────────────
pytest tests/ -m privacy -v                       # privacy/security tests
pytest tests/ -m e2e -v                           # E2E booking + privacy tests
pytest tests/ -m api -v                           # all API tests

# ── Run single test ───────────────────────────────────────────────────────
pytest tests/test_e2e_booking_and_privacy.py::TestCompleteE2EBookingAndPrivacyFlow::test_e2e_1_user_a_advances_booking_to_payment_stage -v

# ── HTML report ───────────────────────────────────────────────────────────
pytest tests/ -v --html=api_test_report.html --self-contained-html
open api_test_report.html
```

---

## 7. How It Works

### Authentication flow

Every test gets a fresh `EzraApiClient` from `conftest.py`:

```
conftest.py
  member_a_client fixture
      │
      ├─ EzraApiClient(username, password)   ← credentials from test_users.json
      ├─ .authenticate()    → POST /connect/token  → stores Bearer token in session
      └─ .get_current_member()  → GET /api/members  → caches member_id
```

The Bearer token is automatically attached to every subsequent request via
`requests.Session` headers — no manual token management needed in tests.

### Privacy test logic

```
Member A's token                  Member B's resources
      │                                    │
      └─── GET /submissions/{B_id}/detail ──► API should return 401/403/404
                                                        ▲
                                               PASS = request blocked
                                               FAIL = 2xx (security hole)
```

### `EzraApiClient` — endpoint map

| Method | HTTP | Path | Needs encounter_id? |
|---|---|---|---|
| `authenticate()` | POST | `/individuals/member/connect/token` | — |
| `get_current_member()` | GET | `/individuals/api/members` | — |
| `mark_booking_stage()` | POST | `/platform/api/members/bookingstage` | ✅ Yes |
| `create_pending_payment()` | POST | `/packages/api/payments/{enc}/create-pending` | ✅ Yes |
| `start_or_fetch_submission()` | POST | `/diagnostics/.../mq/submissions/{m}/{enc}` | ✅ Yes |
| `get_submission_detail()` | GET | `/diagnostics/.../mq/submissions/{id}/detail` | ❌ No |
| `save_submission_answer()` | POST | `/diagnostics/.../mq/submissions/{id}/data` | ❌ No |
| `complete_submission()` | POST | `/diagnostics/.../mq/submissions/{id}/complete` | ❌ No |

---

## 8. Relationship to the Playwright UI Suite

| Aspect | UI suite (`tests/`) | API suite (`api_tests/`) |
|---|---|---|
| **Tool** | Playwright + browser | `requests` (no browser) |
| **Speed** | ~60–120 s per test | ~1–3 s per test |
| **What it tests** | Full user journey through the UI | Backend authorization and data integrity |
| **BUG-03 coverage** | Browser-level ID upload mismatch | API-level cross-member data access |
| **Dependencies** | `playwright`, `pytest` | `requests`, `pytest` |
| **Credentials** | `fixtures/test_users.json` | `fixtures/test_users.json` (same file) |

Both suites are complementary — the UI tests validate the complete user experience
while the API tests provide fast, CI-friendly security regression coverage.

---

*All coding was assisted by **GitHub Copilot** (Claude Sonnet / Haiku) and tests
were generated using the **Playwright MCP server** (`mcp.json`) following the
best-practice rules in `mcp_instructions.md`.*


