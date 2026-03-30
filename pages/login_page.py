"""
Login Page Object
Handles authentication on the Ezra staging website
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Page object for login functionality"""

    # Locators
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    SUBMIT_BUTTON = 'button[type="submit"], button:has-text("Sign In"), button:has-text("Submit")'
    JOIN_BUTTON = (
        'button:has-text("Join"), button:has-text("Sign Up"), '
        'a:has-text("Join"), a:has-text("Sign Up"), :has-text("Don\'t have an account")'
    )

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("LoginPage initialized")

    def is_login_page_displayed(self) -> bool:
        """Verify that the login page is displayed, waiting for the form to render."""
        return self.wait_for_selector(self.EMAIL_INPUT)

    def click_join_button(self):
        """Click the Join/Sign Up button to navigate to the signup page"""
        logger.info("Clicking Join button")
        join_buttons = self.page.locator(self.JOIN_BUTTON)
        if join_buttons.count() == 0:
            raise Exception("Join button not found on login page")
        join_buttons.first.click()
        self.wait_for_navigation()
        logger.info("✓ Navigated to signup page")

    def login(self, username: str, password: str):
        """
        Perform login with credentials

        Args:
            username: Email address
            password: Password
        """
        logger.info("Starting login process")

        if not self.is_element_visible(self.EMAIL_INPUT):
            raise Exception("Email input field not found")
        self.fill(self.EMAIL_INPUT, username)
        logger.info("✓ Email entered")

        if not self.is_element_visible(self.PASSWORD_INPUT):
            raise Exception("Password input field not found")
        self.fill(self.PASSWORD_INPUT, password)
        logger.info("✓ Password entered")

        submit_btn = self.page.locator(self.SUBMIT_BUTTON)
        if submit_btn.count() > 0:
            submit_btn.first.click()
            logger.info("✓ Submit button clicked")
        else:
            logger.warning("Submit button not found, using Enter key as fallback")
            self.page.locator(self.PASSWORD_INPUT).first.press("Enter")

        # Wait for navigation away from the login page
        try:
            self.page.wait_for_url(
                lambda url: "sign-in" not in url.lower(),
                timeout=self.wait_timeout,
            )
            logger.info(f"✓ Login successful. URL: {self.page.url}")
        except PlaywrightTimeoutError:
            logger.warning(f"Login navigation timeout. Current URL: {self.page.url}")
