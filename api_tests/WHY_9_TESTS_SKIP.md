# Why 9 E2E Tests Skip & How to Make Them Pass

## Why They Skip

The 9 E2E tests in `test_e2e_booking_and_privacy.py` are **intentionally skipped** when `encounter_id` is not available.

### What is `encounter_id`?

An **encounter** is a single booked scan appointment created on the backend. Each booking gets a unique UUID.

```
User books MRI Scan via UI  →  Backend creates encounter
                               encounter_id = "550e8400-e29b-41d4-a716-446655440000"
                               Tests can now use this ID
```

### Why Tests Skip Without It

Tests 1-3 need `encounter_id` to:
- Advance booking to PAYMENT_PAGE stage
- Create pending Stripe payment
- Start medical questionnaire

Without it, tests skip gracefully (not fail):

```
SKIPPED: No encounter_id found:
  • ENV VAR: EZRA_ENCOUNTER_ID not set
  • AUTO-FETCH: No bookings found via API
```

---

## Solution: Hybrid Approach ✅

We implemented a **3-priority system** for getting `encounter_id`:

```
1. ENV VAR (fastest)          → export EZRA_ENCOUNTER_ID="uuid"
   ↓ (if not set)
2. AUTO-FETCH (default)       → GET /scheduling/api/appointments/...
   ↓ (if not found)
3. SKIP GRACEFULLY            → Skip with helpful message
```

### How It Works

**Priority 1 — Environment Variable** (Fastest, for CI):
```python
eid = os.getenv("EZRA_ENCOUNTER_ID")  # Check env var first
if eid:
    return eid  # Use it immediately, skip API call
```

**Priority 2 — Auto-Fetch from API** (Default, for local dev):
```python
eid = getattr(client, "latest_encounter_id", None)  # Already fetched by conftest
if eid:
    return eid  # Use it
```

**Priority 3 — Skip Gracefully** (Expected for new users):
```python
pytest.skip("No encounter_id found:\n"
            "  • ENV VAR: EZRA_ENCOUNTER_ID not set\n"
            "  • AUTO-FETCH: No bookings found via API\n")
```

---

## 3 Approaches Compared

| Approach | Setup | Speed | Flexibility | Best For |
|---|---|---|---|---|
| **Auto-Fetch Only** | 0 setup, run UI test | Slow (API call) | Low | Local dev |
| **Env Var Only** | Find & export UUID | Instant | Medium | CI/fast runs |
| **Hybrid** (🎯 Ours) | 0 required setup | Fastest when needed | Maximum | All scenarios |

---

## How to Use

### Option A: Default (Auto-Fetch) — No Setup Required

```bash
# 1. Create a booking (generates encounter_id on backend)
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s

# 2. Run API tests (they auto-fetch the ID)
cd api_tests
pytest tests/test_e2e_booking_and_privacy.py -v

# If tests still skip, it means API endpoint unavailable
```

### Option B: Use Environment Variable — Fast & Reliable

```bash
# 1. Get the encounter_id from anywhere:
#    - UI test logs
#    - Booking confirmation URL
#    - Browser DevTools network tab

# 2. Set it as env var
export EZRA_ENCOUNTER_ID="550e8400-e29b-41d4-a716-446655440000"

# 3. Run tests (uses env var immediately, no API call)
pytest tests/test_e2e_booking_and_privacy.py -v

# Tests now pass (or fail on API validation, proving var is used)
```

### Option C: Hybrid (Recommended)

```bash
# Don't need to do anything special!
# Tests automatically:
# 1. Check for EZRA_ENCOUNTER_ID env var (if set, use it)
# 2. Try to auto-fetch from API (if env var not set)
# 3. Skip gracefully with helpful message (if both fail)

pytest tests/test_e2e_booking_and_privacy.py -v
```

---

## Why Hybrid is Best

✅ **Zero required setup** — Works immediately out of the box
✅ **Flexible** — Can be optimized with env vars when needed
✅ **Fast** — Can skip API calls with env var (useful for CI)
✅ **Graceful** — Clear skip message if nothing found
✅ **No duplication** — Single source of truth
✅ **Works everywhere** — Local dev + CI + staging

---

## Test Results

```bash
$ pytest tests/test_e2e_booking_and_privacy.py -v

# Without env var set:
SKIPPED (9 tests)  — Auto-fetch found no bookings
  Clear message tells user how to fix it

# With env var set:
FAILED (expected)  — Uses env var, API rejects test UUID
  Shows env var is properly accepted

# With real UUID:
PASSED            — All tests run!
```

---

## Summary

| Scenario | What Happens | Your Action |
|----------|---|---|
| Run tests without booking | 9 skip (auto-fetch fails) | Run UI test OR set env var |
| Run tests after UI booking | 9 run (auto-fetch succeeds) | Nothing! |
| Need faster runs (CI) | Set env var, skip auto-fetch | `export EZRA_ENCOUNTER_ID="..."` |
| Don't know the UUID | Still works! | Leave env var unset, auto-fetch handles it |

**The implementation automatically picks the best approach based on what's available.** 🎉

