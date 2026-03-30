"""
Calendar and DateTime Selection Pages
Handles date and time selection for appointment booking
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect
import logging

logger = logging.getLogger(__name__)


class DateTimeSelectionPage(BasePage):
    """Page object for date and time selection"""

    # Supported calendar libraries used by the app.
    # Vue Cal uses .vuecal__* classes; V-Calendar uses .vc-* classes.
    CALENDAR_CONTAINER = '.vuecal, [class*="calendar"], .vc-container'

    # Available (non-disabled) day cells — ordered from most-specific to fallback.
    # Vue Cal: enabled cell content
    DATE_BUTTONS_VUECAL = '.vuecal__cell:not(.vuecal__cell--disabled) .vuecal__cell-content'
    # V-Calendar: enabled day content
    DATE_BUTTONS_VCAL = '.vc-day:not([aria-disabled="true"]) .vc-day-content'
    # Generic date input fallback
    DATE_INPUT = 'input[type="date"]'

    TIME_SLOTS = '.appointments__list label'
    CONTINUE_BUTTON = '[data-test="submit"]'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("DateTimeSelectionPage initialized")

    def is_date_time_selection_displayed(self) -> bool:
        """Verify that the date/time selection page is displayed."""
        try:
            # Wait for page to load
            self.page.wait_for_timeout(2000)
            
            # Try to find calendar or date-related elements
            # Use a longer timeout as this page can take time to render
            try:
                self.page.wait_for_selector(
                    f"{self.CALENDAR_CONTAINER}, {self.DATE_INPUT}, .appointments__list, [class*='date'], [class*='time'], [class*='calendar']",
                    timeout=self.wait_timeout,
                )
                logger.info("✓ Date/time selection page displayed")
                return True
            except PlaywrightTimeoutError:
                logger.warning("Calendar/date selectors not found, trying alternative detection")
                
                # Fallback: check URL or page content
                url = self.page.url.lower()
                if "datetime" in url or "date" in url or "time" in url:
                    logger.info("✓ Date/time selection page detected via URL")
                    return True
                
                # Check for any visible date-related content
                date_elements = self.page.locator('[class*="date"], [class*="time"], [class*="calendar"], .appointments')
                if date_elements.count() > 0:
                    logger.info("✓ Date/time selection page detected via content")
                    return True
                
                logger.warning("Date/time selection not found within timeout")
                return False
        except Exception as e:
            logger.error(f"Error checking date/time selection: {e}")
            return False

    def select_first_available_date(self) -> bool:
        """
        Select the first available (non-disabled) date from the calendar.

        Tries Vue Cal selectors first, then V-Calendar, then a generic fallback.

        Returns:
            True if a date was selected, False otherwise.
        """
        logger.info("Selecting first available date")

        for selector in (self.DATE_BUTTONS_VUECAL, self.DATE_BUTTONS_VCAL):
            try:
                self.page.wait_for_selector(selector, timeout=5000)
                first_date = self.page.locator(selector).first
                date_text = first_date.text_content()
                first_date.click()
                logger.info(f"✓ Date selected: {date_text!r}")
                return True
            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                logger.error(f"Failed to select date with {selector!r}: {e}")
                return False

        logger.warning("No available date cells found with known calendar selectors")
        return False

    def select_first_available_time(self) -> bool:
        """
        Select the first available time slot.

        Returns:
            True if a slot was selected, False otherwise.
        """
        logger.info("Selecting first available time slot")
        try:
            self.page.wait_for_selector(self.TIME_SLOTS, timeout=self.wait_timeout)
            first_slot = self.page.locator(self.TIME_SLOTS).first
            time_text = (first_slot.text_content() or "").strip()
            first_slot.click()
            logger.info(f"✓ Time slot selected: {time_text!r}")
            return True
        except PlaywrightTimeoutError:
            logger.warning("No time slots found within timeout")
            return False
        except Exception as e:
            logger.error(f"Failed to select time slot: {e}")
            return False

    def click_continue(self) -> bool:
        """
        Click the Continue button once it is enabled.

        Returns:
            True on success, False on timeout.
        """
        logger.info("Waiting for Continue button to be enabled")
        try:
            btn = self.page.locator(self.CONTINUE_BUTTON).first
            btn.wait_for(state="visible", timeout=self.wait_timeout)
            expect(btn).to_be_enabled(timeout=self.wait_timeout)
            btn.click()
            self.wait_for_navigation()
            logger.info("✓ Continue button clicked")
            return True
        except PlaywrightTimeoutError:
            logger.error("Continue button did not become enabled within timeout")
            return False
        except Exception as e:
            logger.error(f"Failed to click Continue: {e}")
            return False

