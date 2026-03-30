# Ezra Staging – Playwright Test Suite

End-to-end automation test suite for the **Ezra staging environment**
(`https://myezra-staging.ezra.com`), built with **Playwright + pytest** following the
**Page Object Model (POM)** pattern.

All tests were written with **GitHub Copilot** (powered by **Claude Sonnet 4.5 / Haiku 4.5**)
and generated using the **Playwright MCP server**.

---

## Table of Contents

1. [Project Introduction](#1-project-introduction)
2. [Project Structure](#2-project-structure)
3. [Dependencies & Setup](#3-dependencies--setup)
4. [How to Run Tests](#4-how-to-run-tests)
5. [What Each Test Does](#5-what-each-test-does)
6. [Page Object Model (POM)](#6-page-object-model-pom)
7. [test_users.json – User Fixture File](#7-test_usersjson--user-fixture-file)
8. [Utils – Helpers & Data Managers](#8-utils--helpers--data-managers)
9. [Screenshots – How & When They Are Created](#9-screenshots--how--when-they-are-created)
10. [Playwright MCP Server](#10-playwright-mcp-server)
11. [AI-Assisted Development](#11-ai-assisted-development)
12. [Common Debugging Issues](#12-common-debugging-issues)

---

## 1. Project Introduction

### 🤖 ⭐ AI-DRIVEN PROJECT NOTICE

> **This project is 95% AI-generated using GitHub Copilot & Claude AI**
> 
> **Only ~5% of code was manually written** — exclusively for:
> - ✅ Verifying and testing AI-generated code functionality
> - ✅ Requesting Claude to optimize code at specific bottleneck areas
> - ✅ Helping Playwright MCP server overcome element selection blockers that it couldn't solve independently

### AI Architecture

**AI Models Used:**
- 🔹 **Claude 4.5 (Haiku)** 
- 🔹 **Claude 4.6 (Sonnet)**

**Integration:**
- **GitHub Copilot** — IDE-based AI completion and suggestions, powered by Claude models
- **Playwright MCP Server** — Automated element detection and page interaction via `mcp.json` config
- **MCP Instructions** — Standardized format enforced via `mcp_instructions.md` for all AI queries

### Key Files for AI Setup

| File | Purpose |
|------|---------|
| `mcp.json` | Playwright MCP server configuration and settings |
| `mcp_instructions.md` | Standard format and guidelines for all MCP queries to ensure consistent quality |
| `.github/copilot/instructions.md` | GitHub Copilot behavior guidelines and project-specific best practices |

Every AI-generated query follows the standards in `mcp_instructions.md` to ensure code quality, consistency, and best practices are maintained.

---

## 2. Project Structure

```
Playwrite_project/
│
├── config.py                        # Global config: BASE_URL, timeouts, credentials
├── conftest.py                      # pytest fixtures: browser, page, existing_user, payment_data
├── pytest.ini                       # pytest settings, markers, logging
├── run_all_tests.py                 # Convenience script to run tests with options
├── requirements.txt                 # Python dependencies
├── mcp.json                         # Playwright MCP server config
├── mcp_instructions.md              # Best-practice instructions for MCP queries
│
├── pages/                           # Page Object Model classes
│   ├── base_page.py                 # Base class with shared helpers
│   ├── login_page.py                # Login / sign-in page
│   ├── signup_page.py               # New user sign-up page
│   ├── select_plan_page.py          # DOB + Gender selection (post-signup)
│   ├── booking_pages.py             # Dashboard, ScanSelection, LocationSelection
│   ├── date_time_page.py            # Date & time slot selection
│   └── questionnaire_pages.py       # Medical questionnaire pages
│
├── tests/
│   ├── test_user_login/
│   │   ├── test_signup_new_user.py          # New user signup flow
│   │   └── test_signup_existing_user.py     # Duplicate email error handling
│   └── test_booking/
│       ├── test_booking_appointment_existing_user.py   # Login → book scan (existing user)
│       └── test_signup_and_booking_new_user.py         # Signup → book scan (new user)
│
├── fixtures/
│   └── test_users.json              # Persistent test user registry
│
├── utils/
│   ├── data_helpers.py              # DOB / gender random generators
│   └── user_data_manager.py         # Read/write/generate users in test_users.json
│
└── screenshots/                     # Auto-generated during test runs (git-ignored)
```

---

## 3. Dependencies & Setup

### Prerequisites

- Python 3.8+
- Node.js (required for the Playwright MCP server)
- pip

### Install Python dependencies

```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**

| Package | Purpose |
|---|---|
| `playwright>=1.40.0` | Core browser automation |
| `pytest>=7.4.0` | Test runner |
| `pytest-timeout>=2.1.0` | Per-test timeout enforcement |
| `pytest-html>=3.2.0` | HTML report generation |
| `pytest-xdist>=3.3.0` | Parallel test execution |
| `pytest-cov>=4.1.0` | Code coverage |
| `python-dotenv>=1.0.0` | `.env` file support |
| `colorama>=0.4.6` | Coloured terminal output |

### Install Playwright browsers

```bash
playwright install chromium
```

### Environment variables (optional overrides)

| Variable | Default | Description |
|---|---|---|
| `EZRA_BASE_URL` | `https://myezra-staging.ezra.com` | Target environment URL |
| `HEADLESS` | `false` | `true` = no browser window |
| `TIMEOUT` | `120000` | Global Playwright timeout (ms) |
| `BROWSER_TYPE` | `chromium` | Browser engine |
| `SLOW_MO` | `0` | Milliseconds delay between actions |

Set them inline or via a `.env` file:

```bash
HEADLESS=true EZRA_BASE_URL=https://myezra-staging.ezra.com pytest tests/
```

---

## 4. How to Run Tests

### Run all tests (default — headed browser, verbose)

```bash
python run_all_tests.py
```

or directly with pytest:

```bash
pytest tests/ -v -s
```

### Run all tests in headless mode (no browser window)

```bash
HEADLESS=true pytest tests/ -v -s
```

### Run all tests with headed browser (explicit)

```bash
HEADLESS=false pytest tests/ -v -s
```

### Run a single test file

```bash
# New user signup only
pytest tests/test_user_login/test_signup_new_user.py -v -s

# Existing user booking only
pytest tests/test_booking/test_booking_appointment_existing_user.py -v -s

# Signup + booking combined (new user)
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s

# Duplicate email error test
pytest tests/test_user_login/test_signup_existing_user.py -v -s
```

### Run by marker

```bash
pytest tests/ -m signup -v -s        # All signup tests
pytest tests/ -m booking -v -s       # All booking tests
pytest tests/ -m "signup and booking" -v -s
```

### Run with HTML report

```bash
python run_all_tests.py --report
# or
pytest tests/ -v -s --html=test_report.html --self-contained-html
```

### List all collected tests without running

```bash
python run_all_tests.py --collect
# or
pytest tests/ --collect-only -q
```

### `run_all_tests.py` options summary

```
python run_all_tests.py               # Verbose (default)
python run_all_tests.py --quiet       # Minimal output
python run_all_tests.py --report      # HTML report
python run_all_tests.py --collect     # List tests
python run_all_tests.py --marker signup
python run_all_tests.py --dir tests/test_booking
python run_all_tests.py --help
```

---

## 5. What Each Test Does

### `tests/test_user_login/test_signup_new_user.py`
**Marker:** `@pytest.mark.signup`

Verifies a brand-new user can complete the signup flow end-to-end.

| Step | Action |
|---|---|
| 1 | Generate a new unique user via `UserDataManager` |
| 2 | Navigate to `/join` |
| 3 | Fill first name, last name, email, phone, password |
| 4 | Accept Terms & Conditions checkbox |
| 5 | Submit the form |
| 6 | Assert the app navigates to the Select Plan page |

> The new user is **not** saved to `test_users.json` in this test — saving happens in the combined booking test.

---

### `tests/test_user_login/test_signup_existing_user.py`
**Marker:** `@pytest.mark.signup`

Verifies the app **rejects** a signup attempt with an already-registered email.

| Step | Action |
|---|---|
| 1 | Navigate to the login page |
| 2 | Click **Join** to open the signup page |
| 3 | Fill the form using the **first user from `test_users.json`** (via `existing_user` fixture) |
| 4 | Accept Terms & Conditions |
| 5 | Submit the form |
| 6 | Assert the duplicate-email error message appears |
| 7 | Assert the page does **not** navigate away from `/join` |
| 8 | Save screenshot to `screenshots/duplicate_email_error.png` |

---

### `tests/test_booking/test_booking_appointment_existing_user.py`
**Markers:** `@pytest.mark.booking`, `@pytest.mark.appointment`

Full appointment booking flow for an **existing, already-registered user**.

| Step | Action |
|---|---|
| 1 | Load first user from `test_users.json` via `existing_user` fixture |
| 2 | Navigate to the app and log in |
| 3 | Assert dashboard is shown |
| 4 | Click **Book a Scan** |
| 5 | Select **MRI Scan with Spine** card |
| 6 | Click Continue → Select recommended location |
| 7 | Select first available date and time slot |
| 8 | Fill Stripe test card details (via `payment_data` fixture) |
| 9 | Submit payment |
| 10 | Assert confirmation page URL |
| 11 | Save screenshot to `tests/test_booking/final_page.png` |

---

### `tests/test_booking/test_signup_and_booking_new_user.py`
**Markers:** `@pytest.mark.signup`, `@pytest.mark.booking`

The **most complete test** — signs up a brand-new user and immediately books an appointment in one flow.

| Step | Action |
|---|---|
| 1 | Generate a new unique user via `UserDataManager` |
| 2 | Navigate to `/join` and fill the signup form |
| 3 | Accept Terms & Conditions and submit |
| 4 | Assert navigation to Select Plan page |
| 5 | Save new user to `test_users.json` |
| 6 | Fill **Date of Birth** (random) and **Gender** (random) on the Select Plan page |
| 7 | Select **MRI Scan with Spine** card (this enables the Continue button) |
| 8 | Click Continue → Select recommended location |
| 9 | Select first available date and time slot |
| 10 | Fill Stripe test card details (via `payment_data` fixture) |
| 11 | Submit payment |
| 12 | Assert URL contains `scan-confirm` |
| 13 | Save screenshot to `tests/test_booking/signup_and_booking_completed.png` |

> **Key insight:** On the Select Plan page, the **Continue button stays disabled until an MRI scan card is selected**. DOB/Gender are filled first, then the scan card is clicked, which enables Continue.

---

## 6. Page Object Model (POM)

All UI interactions are encapsulated in **page objects** under `pages/`. Tests never call
Playwright selectors directly — they call named methods on page objects.

### Class hierarchy

```
BasePage (pages/base_page.py)
 ├── LoginPage
 ├── SignupPage
 ├── SelectPlanPage
 ├── DashboardPage
 ├── ScanSelectionPage
 ├── LocationSelectionPage
 ├── DateTimeSelectionPage
 └── PaymentPage
```

### `BasePage` — shared utilities

`BasePage` is the parent of every page class and provides:

| Method | Purpose |
|---|---|
| `navigate_to(url)` | Go to URL, handle cookie banners |
| `click(selector)` | Wait for visibility then click |
| `fill(selector, text)` | Fill an input field |
| `is_element_visible(selector)` | Boolean visibility check |
| `wait_for_navigation()` | Wait for `domcontentloaded` |
| `take_screenshot(name)` | Save a timestamped screenshot |
| `scroll_to_element(selector)` | Scroll an element into view |

### Example — how a test uses POM

```python
# Test code (no selectors visible)
login_page = LoginPage(page)
login_page.navigate_to(BASE_URL)
login_page.login(email, password)

scan_selection = ScanSelectionPage(page)
scan_selection.select_mri_scan()
scan_selection.click_continue()
```

```python
# Inside ScanSelectionPage (selector logic lives here)
MRI_SCAN_CARD = 'div[class*="encounter-card"]:has-text("MRI")'

def select_mri_scan(self):
    mri_card = self.page.locator(self.MRI_SCAN_CARD).first
    mri_card.scroll_into_view_if_needed()
    mri_card.click()
```

### Resilient selectors

Selectors prefer `data-testid` attributes first, then fall back to CSS classes and
`:has-text()` pseudo-selectors to remain robust against minor UI changes:

```python
BOOK_A_SCAN_BUTTON = '[data-testid="book-scan-btn"], button:has-text("Book a Scan")'
```

---

## 7. `test_users.json` – User Fixture File

**Location:** `fixtures/test_users.json`

This file is the **single source of truth** for all test user accounts. It persists
between test runs so the same registered users can be reused across tests.

### Structure

```json
{
  "base_config": {
    "first_name_prefix": "Preet",
    "last_name_prefix":  "Test",
    "email_base":        "amarpreet911+",
    "email_domain":      "@gmail.com",
    "phone":             "1111111111",
    "password_prefix":   "TestPreet@",
    "password_suffix":   "426*"
  },
  "next_user_number": 25,
  "users": [
    {
      "id": 2,
      "first_name": "Robert",
      "last_name":  "blum",
      "email":      "amarpreet911+1@gmail.com",
      "phone":      "1111111111",
      "password":   "Test921@192",
      "created_at": "2026-03-29T10:35:36.934191Z"
    },
    ...
  ]
}
```

### How it is used

| Who uses it | How |
|---|---|
| `existing_user` fixture (`conftest.py`) | Loads `users[0]` — always the first registered user |
| `UserDataManager.generate_user_data()` | Reads `next_user_number` to generate the next unique user |
| `UserDataManager.add_user()` | Appends a newly registered user and increments `next_user_number` |
| `test_signup_and_booking_new_user.py` | Calls `add_user()` after successful signup to persist the account |
| `test_signup_existing_user.py` | Reads the first user's email to test the duplicate-email rejection |
| `test_booking_appointment_existing_user.py` | Reads the first user's credentials to log in |

> **No hardcoded emails or passwords exist in any test file.** Everything is read
> dynamically from `test_users.json`.

---

## 8. Utils – Helpers & Data Managers

### `utils/user_data_manager.py` — `UserDataManager`

Handles all reading and writing to `test_users.json`.

| Method | Description |
|---|---|
| `__init__()` | Loads `fixtures/test_users.json` into memory |
| `generate_user_data()` | Builds a new user dict using `base_config` + `next_user_number` |
| `add_user(user_data)` | Appends user to JSON, increments `next_user_number`, saves file |
| `get_next_user_number()` | Returns the next sequential user ID |
| `get_all_users()` | Returns full list of registered test users |
| `get_latest_user()` | Returns the most recently added user |
| `get_user_by_email(email)` | Looks up a user by email address |

**How user IDs and emails are generated:**

```
base_config.email_base  +  next_user_number  +  base_config.email_domain
"amarpreet911+"         +  "7"               +  "@gmail.com"
→ amarpreet911+7@gmail.com
```

Password uses the same pattern with `*` replaced by the user number:
```
password_prefix + password_suffix(* → number)
"TestPreet@"    + "4267"
→ TestPreet@4267
```

---

### `utils/data_helpers.py`

Stateless helper functions for generating random test data.

| Function | Returns | Description |
|---|---|---|
| `generate_random_dob(start_year, end_year)` | `"MM-DD-YYYY"` | Random DOB between 1910–1990 |
| `select_random_gender()` | `"Male"` or `"Female"` | Randomly picked gender |
| `generate_test_user_dob_gender()` | `{"dob": ..., "gender": ...}` | Both in one call |

These are used by `SelectPlanPage.select_gender_and_dob()` when the test doesn't
supply specific values, ensuring each test run exercises a different DOB/gender combination.

---

## 9. Screenshots – How & When They Are Created

Screenshots are saved in two ways:

### 1. Automatic on test failure (conftest.py)

`conftest.py` captures a screenshot whenever a test fails, saving it to `screenshots/`
with a timestamp so you can inspect the exact browser state at failure time:

```
screenshots/<test_name>_YYYYMMDD_HHMMSS.png
```

### 2. Manual checkpoints inside tests

Tests explicitly call `page.screenshot()` at key milestones:

| Test | Screenshot path | When |
|---|---|---|
| `test_signup_existing_user` | `screenshots/duplicate_email_error.png` | After duplicate-email error appears |
| `test_booking_appointment_existing_user` | `tests/test_booking/final_page.png` | After payment submission |
| `test_signup_and_booking_new_user` | `tests/test_booking/signup_and_booking_completed.png` | After booking confirmed |

### 3. `BasePage.take_screenshot(name)`

Any page object can call `self.take_screenshot("label")` to save a debug snapshot
at any point. The file is saved to `screenshots/label_YYYYMMDD_HHMMSS.png`.

> All screenshot paths are **git-ignored** (`screenshots/`, `tests/**/*.png`) so they
> never get committed to the repository but are always available locally after a run.

---

## 10. Playwright MCP Server

### What is MCP?

The **Model Context Protocol (MCP)** allows an AI assistant to control a live browser
session during test generation. Instead of guessing selectors, the AI can navigate the
actual staging site, inspect elements, and validate steps **before** writing any code.

### Configuration — `mcp.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

This starts a local Playwright MCP server via `npx`. Your AI assistant (Copilot /
Claude) connects to it to control a real Chromium browser during test generation.

### Best-practice instructions — `mcp_instructions.md`

Every query sent to the MCP server was governed by the rules in `mcp_instructions.md`:

```
1. Use Playwright MCP tools to explore and validate steps BEFORE writing code.
2. Use resilient locators where you can.
3. Create Python tests in Page Object Model form and follow the structure throughout.
4. After generating tests, run them. If any fail, fix and re-run until all pass.
5. Close the MCP browser when finished.
```

This ensured that:
- Selectors were **verified against the live site** before being written into page objects
- The POM structure was maintained consistently across all generated tests
- Tests were validated end-to-end before being considered complete

---

## 11. AI-Assisted Development

All test code in this repository was written with **GitHub Copilot** inside JetBrains IDE.

| Component | Model used |
|---|---|
| Test generation & page objects | Claude Sonnet 4.5 |
| Selector debugging & quick fixes | Claude Haiku 4.5 |
| MCP browser exploration | Playwright MCP server (`@playwright/mcp@latest`) |

### Development workflow

```
1. Describe test scenario to Copilot in natural language
         ↓
2. Copilot uses Playwright MCP server to open staging site
         ↓
3. MCP explores the page — finds real selectors, validates steps
         ↓
4. mcp_instructions.md rules are applied (POM, resilient selectors, etc.)
         ↓
5. Copilot generates page object class + test file
         ↓
6. Test is run; failures are debugged and fixed iteratively
         ↓
7. Passing test is committed
```

---

## 12. Common Debugging Issues

### ⚠️ Issue 1: Signup Tests Failing Due to Invalid Auto-Generated Passwords (MOST COMMON)

**Symptom:**
- Signup tests fail with errors like: "Password does not meet requirements"
- Tests work sometimes but fail other times
- Error appears during password validation step on the signup form
- You see continuous sequential number patterns: 123, 456, 789, 666, etc.

**Root Cause:**
The auto-generated passwords in `fixtures/test_users.json` are created using a pattern-based suffix:

```json
"password_suffix": "426*"
```

This creates passwords with **patterned sequential numbers** (42610, 42611, 42612, etc.), which password validators reject because sequential numbers are considered weak and predictable.

**Solution (QUICK FIX):**

Edit `fixtures/test_users.json` and change:
```json
"next_user_number": 60,
```

To a **larger, unique random number** (break the pattern):
```json
"next_user_number": 7829,
```

Any large number works: `500`, `8432`, `12345`, `9999`, etc. The key is to make the password suffix non-sequential.

**Why This Works:**
- Password validators check for sequential patterns (123456, 789, etc.)
- By jumping to a large random number, the suffix becomes non-sequential and unpredictable
- Example generated passwords with new number:
  - `TestPreet@4267829`
  - `TestPreet@4267830`
  - `TestPreet@4267831`
- These non-sequential numbers pass password strength validation

**Steps to Fix:**

1. Open `fixtures/test_users.json`
2. Find the line: `"next_user_number": 60,`
3. Change `60` to any larger unique number (e.g., `7829`)
4. Save the file
5. Re-run signup tests:
   ```bash
   pytest tests/test_user_login/ -v -s
   pytest tests/test_booking/ -v -s
   ```

**Alternative Solution:**
If the issue persists, modify the `password_suffix` pattern itself:
```json
"password_suffix": "SecureP"  // Use letters instead of just numbers
```

---

### Issue 2: Playwright Browser Not Found

**Symptom:**
```
Error: Chromium browser not found
```

**Solution:**
```bash
playwright install chromium
```

---

### Issue 3: Tests Timeout

**Symptom:**
```
pytest.PytestUnraisableExceptionWarning: TimeoutError
```

**Solution:**
- Increase timeout in `config.py`:
  ```python
  TIMEOUT = 180000  # 180 seconds instead of 120
  ```
- Or run with: `TIMEOUT=180000 pytest tests/ -v -s`


---

## Quick Reference

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Run everything (headed)
pytest tests/ -v -s

# Run everything (headless CI mode)
HEADLESS=true pytest tests/ -v -s

# Single test
pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s

# By marker
pytest tests/ -m booking -v -s

# HTML report
pytest tests/ -v -s --html=test_report.html --self-contained-html
```

