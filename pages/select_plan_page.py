"""
Select Plan Page Object
Handles DOB and Gender selection on the select-plan page
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.data_helpers import generate_random_dob, select_random_gender
import logging

logger = logging.getLogger(__name__)


class SelectPlanPage(BasePage):
    """Page object for select plan page with DOB and gender selection"""

    # Locators
    DOB_INPUT = 'input[id="dob"], input[name="dob"], input[placeholder*="dob" i], input[placeholder*="date" i]'
    GENDER_DROPDOWN = '.multiselect, [class*="multiselect"], select[name*="sex" i], select[name*="gender" i]'
    GENDER_MULTISELECT_PLACEHOLDER = '.multiselect__placeholder'
    GENDER_OPTIONS = '.multiselect__element, [role="option"]'
    CONTINUE_BUTTON = 'button:has-text("Continue"), button:has-text("Next"), [data-test="submit"]'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("SelectPlanPage initialized")

    def is_select_plan_page_displayed(self) -> bool:
        """Verify that the select plan page is displayed"""
        dob_visible = self.is_element_visible(self.DOB_INPUT)
        gender_visible = (
            self.is_element_visible(self.GENDER_DROPDOWN)
            or self.is_element_visible(self.GENDER_MULTISELECT_PLACEHOLDER)
        )
        page_on_url = "select-plan" in self.page.url.lower() or "sign-up" in self.page.url.lower()
        is_displayed = dob_visible or gender_visible or page_on_url
        logger.info(
            f"Select Plan page displayed: {is_displayed} "
            f"(DOB: {dob_visible}, Gender: {gender_visible}, URL: {page_on_url})"
        )
        return is_displayed

    def fill_dob(self, dob: str = None) -> bool:
        """
        Fill the date of birth field

        Args:
            dob: Date of birth in MM-DD-YYYY format (if None, generates random)

        Returns:
            True if successful, False otherwise
        """
        if dob is None:
            dob = generate_random_dob()

        logger.info(f"Filling DOB with: {dob}")
        try:
            dob_input = self.page.locator(self.DOB_INPUT)
            if dob_input.count() == 0:
                logger.error("DOB input not found")
                return False

            first = dob_input.first
            
            # Wait for input to be visible
            first.wait_for(state="visible", timeout=self.wait_timeout)
            logger.info("✓ DOB input is visible")
            
            # Click to focus
            first.click()
            self.page.wait_for_timeout(300)
            
            # Clear any existing value
            first.fill("")
            self.page.wait_for_timeout(200)
            
            # Type the DOB with slower delay to ensure all characters are captured
            first.type(dob, delay=150)
            self.page.wait_for_timeout(500)
            
            entered = first.input_value()
            logger.info(f"✓ DOB filled: {entered}")
            return True
        except Exception as e:
            logger.error(f"Error filling DOB: {e}")
            return False

    def select_gender(self, gender: str = None) -> bool:
        """
        Select gender from dropdown (Male or Female).
        If gender is None, randomly selects between Male and Female.

        Args:
            gender: "Male" or "Female" (if None, randomly selected)

        Returns:
            True if successful, False otherwise
        """
        if gender is None:
            gender = select_random_gender()

        logger.info(f"Selecting gender: {gender}")
        try:
            # Wait for page to be ready before clicking
            self.page.wait_for_timeout(500)
            
            # Try multiselect first
            multiselect = self.page.locator('.multiselect')
            if multiselect.count() > 0:
                multiselect.first.wait_for(state="visible", timeout=5000)
                multiselect.first.click()
                logger.info("✓ Multiselect dropdown clicked")
            else:
                # Try regular dropdown
                dropdown = self.page.locator(self.GENDER_DROPDOWN)
                if dropdown.count() == 0:
                    logger.error("No gender selection dropdown found")
                    return False
                dropdown.first.wait_for(state="visible", timeout=5000)
                dropdown.first.click()
                logger.info("✓ Gender dropdown clicked")

            # Wait for options to appear
            self.page.wait_for_timeout(800)

            # Try different selectors to find the option
            for selector in [
                f'.multiselect__element:has-text("{gender}")',
                f'[role="option"]:has-text("{gender}")',
                f'button:has-text("{gender}")',
                f':has-text("{gender}")',
            ]:
                try:
                    options = self.page.locator(selector)
                    if options.count() > 0:
                        options.first.click()
                        logger.info(f"✓ Gender selected: {gender}")
                        self.page.wait_for_timeout(500)
                        return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            logger.warning(f"Could not find gender option: {gender}")
            return False
        except PlaywrightTimeoutError:
            logger.error("Timed out waiting for gender dropdown/options")
            return False
        except Exception as e:
            logger.error(f"Error selecting gender: {e}")
            return False

    def select_gender_and_dob(self, gender: str = None, dob: str = None) -> bool:
        """
        Select both gender and date of birth.

        Args:
            gender: "Male" or "Female" (if None, randomly selected)
            dob: Date of birth in MM-DD-YYYY format (if None, generates random)

        Returns:
            True if both fields were filled successfully
        """
        if gender is None:
            gender = select_random_gender()
        if dob is None:
            dob = generate_random_dob()

        logger.info(f"Filling DOB: {dob}, Gender: {gender}")
        
        # Wait for page to be fully loaded and interactive
        self.page.wait_for_timeout(2000)
        
        # Ensure DOB field is visible and ready
        try:
            dob_field = self.page.locator(self.DOB_INPUT)
            dob_field.first.wait_for(state="visible", timeout=self.wait_timeout)
            logger.info("✓ DOB field is visible")
        except Exception as e:
            logger.warning(f"DOB field visibility check failed: {e}")
        
        # Fill DOB
        dob_ok = self.fill_dob(dob)
        
        # Wait a bit before selecting gender to allow form to update
        self.page.wait_for_timeout(1000)
        
        # Select gender
        gender_ok = self.select_gender(gender)

        if dob_ok and gender_ok:
            logger.info(f"✓ DOB ({dob}) and Gender ({gender}) filled successfully")
            # Wait for form to settle before continuing
            self.page.wait_for_timeout(1500)
            return True

        logger.error(f"Failed to fill all fields - DOB: {dob_ok}, Gender: {gender_ok}")
        return False

    def click_continue(self) -> bool:
        """Click the Continue button and wait for navigation to the next step."""
        logger.info("Clicking Continue button")
        try:
            btn = self.page.locator(self.CONTINUE_BUTTON)
            if btn.count() == 0:
                for alt in ['button[type="submit"]', 'button:visible']:
                    alt_btn = self.page.locator(alt)
                    if alt_btn.count() > 0:
                        alt_btn.first.click()
                        self.wait_for_navigation()
                        logger.info("✓ Continue clicked (alternative selector)")
                        return True
                logger.error("Continue button not found")
                return False

            btn.first.click()
            self.wait_for_navigation()
            logger.info("✓ Continue button clicked")
            return True
        except Exception as e:
            logger.error(f"Error clicking Continue: {e}")
            return False

