# Git Repository Structure & Documentation Guide

---

## 🤖 ⭐ AI-DRIVEN PROJECT NOTICE

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
- **GitHub Copilot** — IDE-based AI completion and suggestions
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

## 📚 README Files & Their Purposes

---
### 1. **TEST_SETUP_AND_README.md**
**Location:** `Playwrite_project/TEST_SETUP_AND_README.md`

**Purpose:** Main documentation guide for the entire test suite. Complete overview of the entire test suite structure
**Contains:**
- Overview of the project (Playwright + API testing)
- Quick start instructions
- Test execution examples: `pytest tests/ -v -s`
- Directory structure and file organization
- How to set up the environment and fixtures
- Project architecture and capabilities
- Test organization and categorization
- How tests are structured and executed
- Overall test capabilities and what's covered

---
### 2. **BUG_REPORT.md**
**Location:** `/Users/amarpreetsingh/IdeaProjects/Playwrite_project/BUG_REPORT.md`

**Purpose:** Known issues, bugs, and tracking for the booking/questionnaire flows
**Contains:**
- Documented bugs in the Ezra booking system
- Bug tracking and reproduction steps
- Known issues in:
  - Height/weight field interactions
  - Date selection edge cases
  - Questionnaire completion requirements
  - Other UI/UX issues found during testing

**Bug Resources:** `/Users/amarpreetsingh/IdeaProjects/Playwrite_project/bug_resources/`
- Screenshots and videos demonstrating each bug
- Visual evidence of issues found

---

### 3. **api_tests/README.md** 
**Location:** `/Users/amarpreetsingh/IdeaProjects/Playwrite_project/api_tests/README.md`

**Purpose:** Complete API test suite documentation (590 lines)
**Contains:**
- Purpose of API tests (3 security tests + 9 E2E tests = 12 total)
- Package structure with file organization
- Where user data comes from (fixtures/test_users.json)
- What is an Encounter ID and how it's fetched automatically
- Setup instructions for API testing
- How to Run section with 9 subsections:
  - All API tests
  - Booking flow tests only
  - Privacy/security tests only
  - Single test execution
  - E2E story script
  - Running by pytest marker
  - HTML report generation
  - Quick-reference cheat sheet
- How It Works (authentication flow, privacy test logic, endpoint map)
- Relationship to Playwright UI Suite

**Key Data Held:**
```
User credentials from fixtures/test_users.json:
- User 1: amarpreet911+1@gmail.com (Robert blum)
- User 2: amarpreet911+3@gmail.com (Preet3 Test3)

Encounter ID: Auto-fetched from API after login
Submission ID: Captured dynamically from API responses

Test counts:
- test_questionnaire_privacy.py: 3 security tests (✅ always passing)
- test_e2e_booking_and_privacy.py: 9 E2E tests (skip if no bookings)
```

---


### 4. **api_tests/SOME_PRIVACY_SCENARIOS.md**
**Location:** `/Users/amarpreetsingh/IdeaProjects/Playwrite_project/api_tests/SOME_PRIVACY_SCENARIOS.md`

**Purpose:** Detailed documentation of privacy and security test scenarios
**Contains:**
- Security test scenarios for cross-member data access
- Validation cases that ensure members cannot access other members' data:
  - Cannot read another member's questionnaire
  - Cannot write to another member's questionnaire
  - Cannot complete another member's questionnaire
- How privacy violations are detected and reported

---


## 🔧 Test Data Files

### **fixtures/test_users.json**
**Location:** `/Users/amarpreetsingh/IdeaProjects/Playwrite_project/fixtures/test_users.json`

**Purpose:** Pre-configured test user credentials and medical information
**Data Holds:**
```json
{
  "users": [
    {
      "id": 2,
      "first_name": "Robert",
      "last_name": "blum",
      "email": "amarpreet911+1@gmail.com",
      "phone": "1111111111",
      "password": "Test921@192"
    },
    {
      "id": 3,
      "first_name": "Preet3",
      "last_name": "Test3",
      "email": "amarpreet911+3@gmail.com",
      "phone": "1111111111",
      "password": "TestPreet@4263"
    }
  ]
}
```

**Note:** No submission_id or encounter_id needed — these are fetched dynamically from API responses

---

## 📋 Configuration Files

### **api_tests/README.md** Continued - Execution Quick Reference

**To update commit message:**
```bash
cd /Users/amarpreetsingh/IdeaProjects/Playwrite_project
git commit --amend -F COMMIT_MESSAGE.txt
```

**To run UI tests:**
```bash
cd ..
pytest tests/ -v -s                 # All UI tests
pytest tests/test_booking/ -v -s    # Booking tests only
pytest tests/test_user_login/ -v -s # Login/signup tests only
```

**To run API tests:**
```bash
cd api_tests
pytest tests/ -v                    # All 12 tests
pytest tests/ -m privacy -v         # Security tests only (3 tests)
pytest tests/ -m e2e -v             # E2E booking+privacy (9 tests) [WIP will skip as need more data to handle payload created on fly]
```

---

## 🎯 Summary

| File | Lines | Type | Focus |
|------|-------|------|-------|
| **README.md** | ~50 | Main Guide | UI tests execution |
| **api_tests/README.md** | **590** | Comprehensive | API tests, setup, troubleshooting |
| **TEST_SUITE_README.md** | Variable | Architecture | Overall structure |
| **api_tests/SOME_PRIVACY_SCENARIOS.md** | Variable | Security | Privacy test scenarios |
| **BUG_REPORT.md** | Variable | Bugs | Known issues in Ezra |

---

## 📝 Updated Commit Message
- Contains details on work included in the repository.

---

## How to Apply the New Commit Message

Once you have a clean shell, run:
```bash
cd /Users/amarpreetsingh/IdeaProjects/Playwrite_project
git commit --amend -F COMMIT_MESSAGE.txt
```

This will update your initial commit with the comprehensive message.

