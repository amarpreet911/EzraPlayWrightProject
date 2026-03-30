"""
Configuration module for Ezra Booking Tests
Stores environment variables and configuration settings
"""

import os
from typing import Optional

# Test environment variables (use environment variables in production)
BASE_URL = os.getenv("EZRA_BASE_URL", "https://myezra-staging.ezra.com")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # Set to False for visible browser
TIMEOUT = int(os.getenv("TIMEOUT", "120000"))  # 120 seconds for slow airplane WiFi

# Credentials (should be stored in environment variables in production)
TEST_USERNAME = os.getenv("TEST_USERNAME", "amarpreet911+1@gmail.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test921@192")

# Playwright configuration
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")
SLOW_MO = int(os.getenv("SLOW_MO", "0"))

# Test configuration - increased for slow networks
WAIT_FOR_SELECTOR_TIMEOUT = int(os.getenv("WAIT_FOR_SELECTOR_TIMEOUT", "60000"))  # 60 seconds
WAIT_FOR_NAVIGATION_TIMEOUT = int(os.getenv("WAIT_FOR_NAVIGATION_TIMEOUT", "120000"))  # 120 seconds
ELEMENT_CLICK_TIMEOUT = int(os.getenv("ELEMENT_CLICK_TIMEOUT", "60000"))  # 60 seconds

# Screenshot and logging
SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
SCREENSHOTS_DIR = "screenshots"
LOGS_DIR = "logs"

# Create required directories
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


