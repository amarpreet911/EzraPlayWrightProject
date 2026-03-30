"""
Dashboard and Booking Pages
Handles navigation and booking selection
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger(__name__)


class DashboardPage(BasePage):
    """Page object for the dashboard after login"""

    # Prefer data-testid; fall back to visible text for resilience
    BOOK_A_SCAN_BUTTON = '[data-testid="book-scan-btn"], button:has-text("Book a Scan"), a:has-text("Book a Scan")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("DashboardPage initialized")

    def is_dashboard_displayed(self) -> bool:
        """Verify that the dashboard is displayed by checking the URL and waiting for content."""
        try:
            url = self.page.url.lower()
            # Dashboard is reached if we're not on login/signup pages
            is_dashboard = "sign-in" not in url and "join" not in url and "sign-up" not in url
            
            if is_dashboard:
                # Wait for the page to fully render - give Vue.js time to render dashboard content
                logger.info("Dashboard URL confirmed, waiting for content to render...")
                self.page.wait_for_timeout(2000)  # Give Vue.js time to render
                
                # Try to wait for any booking-related content
                try:
                    # Look for scan cards, appointment info, or booking CTAs
                    self.page.wait_for_selector(
                        "button, div[role='button'], [data-testid], h1, h2", 
                        timeout=5000
                    )
                except:
                    pass  # Content may still be loading, that's okay
                
                logger.info("✓ Dashboard displayed (URL-based check)")
                return True
            
            logger.warning(f"Not on dashboard page. URL: {url}")
            return False
        except Exception as e:
            logger.error(f"Error checking dashboard: {e}")
            return False

    def click_book_a_scan(self):
        """Click the 'Book a Scan' button and wait for navigation."""
        logger.info("Clicking 'Book a Scan' button")
        
        # Wait a bit for page to fully render
        self.page.wait_for_timeout(1000)
        
        # Find the button by data-testid (there may be 2, we need the visible one)
        buttons = self.page.locator('[data-testid="book-scan-btn"]')
        logger.info(f"Found {buttons.count()} button(s) with data-testid='book-scan-btn'")
        
        # Click the first visible and enabled button
        clicked = False
        for i in range(buttons.count()):
            btn = buttons.nth(i)
            is_visible = btn.is_visible()
            is_enabled = btn.is_enabled()
            text = btn.text_content().strip()
            logger.info(f"  Button {i}: visible={is_visible}, enabled={is_enabled}, text='{text}'")
            
            if is_visible and is_enabled:
                btn.click()
                logger.info(f"✓ Book a Scan clicked (button {i})")
                clicked = True
                break
        
        if not clicked:
            logger.error("No visible, enabled 'Book a Scan' button found")
            raise Exception("Could not find enabled 'Book a Scan' button on dashboard")
        
        self.wait_for_navigation()
        logger.info("✓ Navigation completed after Book a Scan click")


class ScanSelectionPage(BasePage):
    """Page object for scan type selection"""

    # A generic heading/section that is always present on this page
    PAGE_INDICATOR = ':has-text("MRI"), :has-text("Heart"), :has-text("Scan")'
    # Target the encounter card that contains the MRI Scan - use more specific selector with fallbacks
    MRI_SCAN_CARD = 'div[class*="encounter-card"], div[class*="scan-card"], div[class*="card"]:has-text("MRI Scan")'
    MRI_TITLE = '.encounter-card__title:has-text("MRI Scan with Spine"), .encounter-title:has-text("MRI")'
    CONTINUE_BUTTON = 'button:has-text("Continue"), [role="button"]:has-text("Continue")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("ScanSelectionPage initialized")

    def is_scan_selection_displayed(self) -> bool:
        """Verify that the scan-selection page is displayed."""
        try:
            self.page.wait_for_selector(self.MRI_SCAN_CARD, timeout=self.wait_timeout)
            logger.info("✓ Scan selection page displayed")
            return True
        except PlaywrightTimeoutError:
            logger.warning("Scan selection not found within timeout")
            return False

    def select_mri_scan(self):
        """Select the MRI Scan option - wait for page load before clicking."""
        logger.info("Selecting MRI Scan")
        
        # Wait for page to fully load and render
        self.page.wait_for_timeout(3000)
        
        # Try multiple selector strategies to find the MRI card
        selectors = [
            'div[class*="encounter-card"]:has-text("MRI")',
            'div[class*="scan-card"]:has-text("MRI")',
            'div[class*="card"]:has-text("MRI Scan")',
            'div:has-text("MRI Scan with Spine")',
            'div:has-text("MRI Scan")'
        ]
        
        mri_card = None
        for selector in selectors:
            try:
                card = self.page.locator(selector)
                count = card.count()
                if count > 0:
                    logger.info(f"Found {count} card(s) using selector: {selector}")
                    # Verify it's actually visible
                    if card.first.is_visible():
                        mri_card = card.first
                        logger.info(f"✓ Using selector: {selector}")
                        break
            except Exception as e:
                logger.debug(f"Selector failed: {selector} - {e}")
                continue
        
        if not mri_card:
            logger.error("Could not find visible MRI Scan card with any selector")
            raise Exception("MRI Scan card not found or not visible")
        
        # Wait for the card to be fully visible and interactive
        try:
            mri_card.wait_for(state="visible", timeout=self.wait_timeout)
            logger.info("MRI Scan card is visible and ready to click")
        except Exception as e:
            logger.error(f"MRI Scan card not ready: {e}")
            raise
        
        # Scroll into view if needed
        try:
            mri_card.scroll_into_view_if_needed()
            logger.info("Scrolled MRI card into view")
        except:
            pass
        
        # Click the card
        logger.info("Clicking MRI Scan card...")
        try:
            mri_card.click()
            logger.info("✓ Clicked MRI Scan card")
        except Exception as e:
            logger.error(f"Failed to click MRI card: {e}")
            # Try clicking with force if first attempt fails
            try:
                mri_card.click(force=True)
                logger.info("✓ Clicked MRI Scan card (with force)")
            except Exception as e2:
                logger.error(f"Failed to click MRI card even with force: {e2}")
                raise
        
        # Wait for the UI to register the click
        self.page.wait_for_timeout(2000)
        logger.info("✓ MRI Scan selected")

    def click_continue(self):
        """Click Continue and wait for navigation."""
        logger.info("Clicking Continue on scan selection")
        
        # Wait for page to be fully loaded
        self.page.wait_for_timeout(1000)
        
        # Get the Continue button
        continue_btn = self.page.locator(self.CONTINUE_BUTTON).first
        
        # Wait for page to be interactive before clicking
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except:
            self.page.wait_for_timeout(500)
        
        # Click the button
        logger.info("Clicking Continue button...")
        continue_btn.click()
        self.wait_for_navigation()
        logger.info("✓ Navigation completed after scan selection")


class LocationSelectionPage(BasePage):
    """Page object for clinic location selection"""

    RECOMMENDED_LOCATION = ':has-text("Recommended")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("LocationSelectionPage initialized")

    def is_location_selection_displayed(self) -> bool:
        """Verify that the location-selection page is displayed."""
        try:
            self.page.wait_for_selector(self.RECOMMENDED_LOCATION, timeout=self.wait_timeout)
            logger.info("✓ Location selection page displayed")
            return True
        except PlaywrightTimeoutError:
            logger.warning("Location selection not found within timeout")
            return False

    def select_recommended_location(self):
        """Click the first recommended location card - wait for page load before clicking."""
        logger.info("Selecting recommended location")
        
        # Wait for page to fully load
        self.page.wait_for_timeout(3000)
        
        # Verify location card is visible
        location_card = self.page.locator(self.RECOMMENDED_LOCATION)
        try:
            location_card.first.wait_for(state="visible", timeout=self.wait_timeout)
            logger.info("Recommended location card is visible")
        except Exception as e:
            logger.error(f"Location card not visible: {e}")
            raise
        
        # Click the card
        logger.info("Clicking recommended location card...")
        location_card.first.click()
        
        # Wait for the UI to register the click
        self.page.wait_for_timeout(2000)
        logger.info("✓ Recommended location selected")

    def get_recommended_address(self) -> str:
        """Return the text of the recommended location element."""
        return self.get_text(self.RECOMMENDED_LOCATION)
