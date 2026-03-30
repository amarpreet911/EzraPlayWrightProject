"""
Base Page Object Model class
Provides common functionality for all page objects
"""

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects with common methods"""

    def __init__(self, page: Page, wait_timeout: int = 15000):
        """
        Initialize the base page

        Args:
            page: Playwright Page object
            wait_timeout: Default timeout for waiting (in milliseconds)
        """
        self.page = page
        self.wait_timeout = wait_timeout

    def navigate_to(self, url: str):
        """Navigate to a URL and wait for the page to load"""
        logger.info(f"Navigating to {url}")
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=self.wait_timeout)
        except PlaywrightTimeoutError:
            logger.warning("domcontentloaded timed out, proceeding anyway")

        # Handle cookie consent banner if it appears
        for selector in [
            'button:has-text("Accept")',
            'button:has-text("Agree")',
            'button:has-text("OK")',
            '[data-testid*="cookie" i]',
        ]:
            try:
                btn = self.page.locator(selector)
                if btn.count() > 0 and btn.first.is_visible():
                    logger.info("Accepting cookie consent")
                    btn.first.click()
                    self.page.wait_for_timeout(1000)
                    break
            except Exception as e:
                logger.debug(f"Cookie button check failed for {selector}: {e}")

        logger.info(f"Successfully navigated to {url}")

    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to be visible

        Args:
            selector: CSS selector
            timeout: Optional timeout override

        Returns:
            True if element is found, False otherwise
        """
        try:
            self.page.wait_for_selector(selector, timeout=timeout or self.wait_timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Element not found within timeout: {selector}")
            return False

    def get_element(self, selector: str) -> Locator:
        """Get a Locator for an element"""
        return self.page.locator(selector)

    def click(self, selector: str, timeout: Optional[int] = None):
        """
        Click an element, waiting for it to be enabled first

        Args:
            selector: CSS selector
            timeout: Optional timeout override
        """
        logger.info(f"Clicking element: {selector}")
        timeout_ms = timeout or self.wait_timeout
        locator = self.page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout_ms)
        locator.click()
        logger.info(f"Successfully clicked: {selector}")

    def click_when_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Click an element when it becomes enabled

        Args:
            selector: CSS selector
            timeout: Optional timeout override
        """
        logger.info(f"Waiting for element to be enabled: {selector}")
        timeout_ms = timeout or self.wait_timeout
        try:
            locator = self.page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout_ms)
            locator.click()
            logger.info(f"Successfully clicked enabled element: {selector}")
            return True
        except PlaywrightTimeoutError:
            logger.error(f"Element did not become enabled within timeout: {selector}")
            return False

    def fill(self, selector: str, text: str):
        """
        Fill a text input field

        Args:
            selector: CSS selector
            text: Text to fill
        """
        logger.info(f"Filling text field: {selector}")
        locator = self.page.locator(selector)
        if locator.count() > 0:
            locator.first.fill(text)
            logger.info(f"Successfully filled: {selector}")
        else:
            raise Exception(f"Text field not found: {selector}")

    def get_text(self, selector: str) -> str:
        """Get text content of an element"""
        locator = self.page.locator(selector)
        if locator.count() > 0:
            return locator.first.text_content() or ""
        return ""

    def is_element_visible(self, selector: str) -> bool:
        """Check if an element is currently visible on the page"""
        try:
            locator = self.page.locator(selector)
            return locator.count() > 0 and locator.first.is_visible()
        except PlaywrightTimeoutError:
            return False
        except Exception:
            return False

    def get_input_value(self, selector: str) -> str:
        """Get the value of an input element"""
        locator = self.page.locator(selector)
        if locator.count() > 0:
            return locator.first.input_value() or ""
        return ""

    def wait_for_navigation(self, timeout: Optional[int] = None):
        """Wait for page navigation to complete"""
        logger.info("Waiting for navigation")
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout or self.wait_timeout)
        except PlaywrightTimeoutError:
            logger.warning("Navigation wait timed out, proceeding")
        logger.info("Navigation completed")

    def take_screenshot(self, name: str):
        """Take a screenshot for debugging"""
        import os
        from datetime import datetime

        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.page.screenshot(path=filename)
        logger.info(f"Screenshot saved: {filename}")

    def get_page_title(self) -> str:
        """Get the page title"""
        return self.page.title()

    def get_url(self) -> str:
        """Get the current URL"""
        return self.page.url

    def get_element_count(self, selector: str) -> int:
        """Get count of elements matching selector"""
        return self.page.locator(selector).count()

    def scroll_to_element(self, selector: str):
        """Scroll to an element"""
        locator = self.page.locator(selector)
        if locator.count() > 0:
            locator.first.scroll_into_view_if_needed()
            logger.info(f"Scrolled to element: {selector}")

