"""
Signup/Join Page Object
Handles user registration on the Ezra staging website
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect
import logging

logger = logging.getLogger(__name__)


class SignupPage(BasePage):
    """Page object for signup/join functionality"""

    # Locators
    FIRST_NAME_INPUT = 'input[name*="first" i], input[placeholder*="first" i], input[id*="first" i]'
    LAST_NAME_INPUT = 'input[name*="last" i], input[placeholder*="last" i], input[id*="last" i]'
    EMAIL_INPUT = 'input[type="email"], input[name*="email" i], input[placeholder*="email" i]'
    PHONE_INPUT = 'input[type="tel"], input[name*="phone" i], input[placeholder*="phone" i]'
    PASSWORD_INPUT = 'input[type="password"], input[name*="password" i], input[placeholder*="password" i]'
    TERMS_CHECKBOX = 'input[type="checkbox"], [role="checkbox"]'
    SUBMIT_BUTTON = (
        'button[type="submit"], button:has-text("Submit"), button:has-text("Join"), '
        'button:has-text("Sign Up"), button:has-text("Create Account")'
    )
    TERMS_TEXT = ':has-text("terms"), :has-text("Terms"), :has-text("agreement")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("SignupPage initialized")

    def is_signup_page_displayed(self) -> bool:
        """Verify that the signup page is displayed, waiting for the form to render."""
        return self.wait_for_selector(self.EMAIL_INPUT)

    def fill_signup_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
    ):
        """
        Fill the signup form with user information.

        Args:
            first_name: Legal first name
            last_name: Last name
            email: Email address
            phone: Phone number
            password: Password
        """
        logger.info("Starting form fill process")

        for field, selector, label in [
            (first_name, self.FIRST_NAME_INPUT, "first name"),
            (last_name, self.LAST_NAME_INPUT, "last name"),
            (email, self.EMAIL_INPUT, "email"),
            (phone, self.PHONE_INPUT, "phone"),
            (password, self.PASSWORD_INPUT, "password"),
        ]:
            logger.info(f"Filling {label}")
            self.fill(selector, field)
            logger.info(f"✓ {label.capitalize()} filled")

    def check_terms_agreement(self):
        """Check the 'I agree to Ezra's terms of use' checkbox"""
        logger.info("Checking terms agreement checkbox")

        try:
            # Wait for page to be ready
            self.page.wait_for_timeout(1000)
            
            # Find the span with terms text and click its parent button
            marketing_span = self.page.locator(
                'span:has-text("I agree to Ezra\'s terms of use, telehealth policy")'
            )
            if marketing_span.count() > 0:
                # Get the parent button and click it
                checkbox_button = marketing_span.first.locator("..")  # Parent element
                checkbox_button.click()
                logger.info("✓ Terms checkbox clicked (parent button)")
                
                # Wait for checkbox state to update
                self.page.wait_for_timeout(500)
                return

            logger.warning("⚠️ Could not find terms checkbox span")
            
            # Fallback: Try to find button.checkbox directly
            checkbox = self.page.locator('button.checkbox')
            if checkbox.count() > 0:
                # Click the first checkbox button (should be the terms one)
                checkbox.first.click()
                logger.info("✓ Terms checkbox clicked (fallback button.checkbox)")
                self.page.wait_for_timeout(500)
                return
            
            logger.error("⚠️ Could not find terms checkbox with any method")

        except Exception as e:
            logger.error(f"Error checking terms agreement: {e}")

    def wait_for_submit_enabled(self, max_wait: int = 15) -> bool:
        """
        Wait for the submit button to become enabled.

        Args:
            max_wait: Maximum wait time in seconds.

        Returns:
            True if button becomes enabled within the timeout, False otherwise.
        """
        logger.info(f"Waiting up to {max_wait}s for submit button to be enabled")
        
        # Give the form time to validate all fields
        self.page.wait_for_timeout(1000)
        
        try:
            btn = self.page.locator(self.SUBMIT_BUTTON).first
            expect(btn).to_be_enabled(timeout=max_wait * 1000)
            logger.info("✓ Submit button is enabled")
            return True
        except (PlaywrightTimeoutError, AssertionError):
            logger.warning(f"Submit button not enabled within {max_wait}s")
            return False

    def click_submit_button(self):
        """Click the submit button"""
        logger.info("Clicking submit button")
        
        # Wait a bit before clicking to ensure form is ready
        self.page.wait_for_timeout(500)
        self.page.locator(self.SUBMIT_BUTTON).first.click()
        logger.info("✓ Submit button clicked")

    def submit_form(self) -> bool:
        """
        Wait for submit button to be enabled then click it.

        Returns:
            True if the button was found and clicked, False otherwise.
        """
        logger.info("Submitting signup form")
        if self.wait_for_submit_enabled():
            self.click_submit_button()
            logger.info("✓ Form submitted")
            return True
        logger.error("Submit button was not enabled — form not submitted")
        return False

    def wait_for_signup_confirmation(self, max_wait: int = 30) -> bool:
        """
        Wait until the browser navigates away from the signup/join page to
        the 'select-plan' (or equivalent post-signup) page.

        Args:
            max_wait: Maximum wait time in seconds (default 30s for slow staging).

        Returns:
            True if the plan-selection page is reached, False on timeout.
        """
        logger.info(f"Waiting up to {max_wait}s for signup confirmation (select-plan page)")
        initial_url = self.page.url
        logger.info(f"Initial URL: {initial_url}")

        try:
            self.page.wait_for_url(
                lambda url: any(
                    kw in url.lower() for kw in ["plan", "select", "sign-up"]
                ),
                timeout=max_wait * 1000,
            )
            logger.info(f"✓ Signup confirmed — URL: {self.page.url}")
            return True
        except PlaywrightTimeoutError:
            logger.error(
                f"Did not reach select-plan page within {max_wait}s. "
                f"Current URL: {self.page.url}"
            )
            return False

    def wait_for_duplicate_email_error(self, max_wait: int = 10) -> bool:
        """
        Wait for the duplicate-email error message:
        "If you have previously created an account try logging in instead."

        Args:
            max_wait: Maximum wait time in seconds.

        Returns:
            True if the error message is detected, False on timeout.
        """
        logger.info(f"Waiting up to {max_wait}s for duplicate-email error")

        # Build a combined CSS selector for all known error patterns
        error_texts = [
            "previously created an account",
            "try logging in",
            "account already exists",
            "email already registered",
            "email is already in use",
        ]
        # Use Playwright's :text() pseudo-class for each phrase
        combined = ", ".join(f':text("{t}")' for t in error_texts)

        try:
            self.page.wait_for_selector(combined, timeout=max_wait * 1000)
            logger.info("✓ Duplicate-email error message found")
            return True
        except PlaywrightTimeoutError:
            pass

        # Fallback: check for error-styled inputs
        try:
            self.page.wait_for_selector(
                'input[aria-invalid="true"], input.error, .error-input',
                timeout=2000,
            )
            logger.info("✓ Error-styled input found (duplicate-email indicator)")
            return True
        except PlaywrightTimeoutError:
            pass

        logger.warning("Duplicate-email error not detected")
        return False
