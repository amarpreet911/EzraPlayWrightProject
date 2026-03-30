"""
Pytest configuration and fixtures for Page Object Model framework
Handles browser setup/teardown and common test utilities
"""

import pytest
import logging
import os
import json
from typing import Iterator
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config import BASE_URL, HEADLESS, TIMEOUT
from utils.user_data_manager import UserDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Hook: capture per-phase outcome so fixtures can check if a test passed/failed
# ──────────────────────────────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store the call-phase report on the test item so fixtures can access it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ──────────────────────────────────────────────────────────────────────────────
# Browser / page fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """
    Session-scoped fixture that provides a Playwright Chromium browser instance.

    Yields:
        Browser: Chromium browser instance
    """
    logger.info("Starting Playwright browser...")
    playwright = sync_playwright().start()
    _browser = playwright.chromium.launch(headless=HEADLESS)

    yield _browser

    logger.info("Closing Playwright browser...")
    _browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def page(browser: Browser) -> Iterator[Page]:
    """
    Function-scoped fixture that provides a fresh page for each test.
    Sets the global default timeout from config so every Playwright call
    respects it without needing explicit per-call overrides.

    Args:
        browser: Session-scoped browser fixture

    Yields:
        Page: Playwright page instance
    """
    logger.info("Creating new browser page...")
    context: BrowserContext = browser.new_context()
    # Apply the global timeout to every locator / navigation call
    context.set_default_timeout(TIMEOUT)
    _page = context.new_page()

    yield _page

    logger.info("Closing browser page...")
    _page.close()
    context.close()


# ──────────────────────────────────────────────────────────────────────────────
# User data fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def existing_user() -> dict:
    """
    Fixture providing the first registered user from test_users.json.
    Use this whenever a test needs to log in with an already-existing account.

    Returns:
        dict: User credentials (email, password, …)

    Raises:
        ValueError: If test_users.json contains no users.
    """
    json_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures", "test_users.json"
    )
    with open(json_file, "r") as f:
        data = json.load(f)

    users = data.get("users", [])
    if not users:
        raise ValueError(
            "No users found in fixtures/test_users.json. "
            "Run the new-user signup test first to populate it."
        )

    user = users[0]
    logger.info(f"existing_user fixture: loaded user '{user['email']}'")
    return user


@pytest.fixture(scope="function")
def test_user():
    """
    Fixture providing generic test user credentials.

    Returns:
        dict: User credentials
    """
    return {
        "username": "test@example.com",
        "password": "Test@1234"
    }


@pytest.fixture(scope="function")
def payment_data():
    """
    Fixture providing test payment data (Stripe test card).

    Returns:
        dict: Payment information
    """
    return {
        "card_number": "4242424242424242",
        "expiry_month": "03",
        "expiry_year": "29",
        "cvc": "123",
        "country": "United States",
        "postal_code": "98101"
    }


@pytest.fixture(scope="function")
def new_user_data(request):
    """
    Fixture providing freshly-generated new user data for signup tests.
    Saves the user to test_users.json ONLY when the test passes.

    Returns:
        dict: New user credentials
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file = os.path.join(current_dir, "fixtures", "test_users.json")

        manager = UserDataManager(json_file)
        user_data = manager.generate_user_data()
        logger.info(f"Generated new user data: {user_data['first_name']} {user_data['last_name']}")

        yield user_data

        # Save user only if the test call phase passed.
        # pytest_runtest_makereport sets rep_call on the item after execution.
        rep_call = getattr(request.node, "rep_call", None)
        test_passed = rep_call is not None and rep_call.passed

        if test_passed:
            logger.info("✓ Test PASSED — saving new user to JSON")
            manager.add_user(user_data)
        else:
            logger.warning("✗ Test did not pass — new user NOT saved")

    except Exception as e:
        logger.error(f"Error in new_user_data fixture: {e}")
        raise


# ──────────────────────────────────────────────────────────────────────────────
# Pytest hooks
# ──────────────────────────────────────────────────────────────────────────────
def pytest_configure(config):
    """Initial configuration log."""
    logger.info("=" * 70)
    logger.info("Starting Test Suite - Appointment Booking Automation")
    logger.info("=" * 70)
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"Headless: {HEADLESS}")
    logger.info(f"Timeout: {TIMEOUT}ms")
    logger.info("=" * 70)


def pytest_ignore_collect(collection_path: Path, config) -> bool:
    """Skip deprecated test directories."""
    path_str = str(collection_path)
    if "test_select_plan" in path_str or "test_dob_sex_selection" in path_str:
        return True
    return False


def pytest_collection_modifyitems(config, items):
    """Auto-add markers based on test node IDs."""
    for item in items:
        nid = item.nodeid
        for marker in ("booking", "payment", "appointment", "signup"):
            if marker in nid:
                item.add_marker(getattr(pytest.mark, marker))
