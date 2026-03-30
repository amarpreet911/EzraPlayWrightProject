"""
Payment and Questionnaire Pages
Handles payment selection and medical questionnaire flow
"""

from pages.base_page import BasePage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger(__name__)


class PaymentPage(BasePage):
    """Page object for payment - handles Stripe Payment Element"""

    # Locators
    CONTINUE_BUTTON = '[data-test="submit"]'
    PAYMENT_ELEMENT = '#payment-element'
    PAYMENT_FORM = '#payment-form'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("PaymentPage initialized")

    def is_payment_page_displayed(self) -> bool:
        """Verify that payment page is displayed"""
        try:
            self.page.wait_for_selector(
                f"{self.PAYMENT_ELEMENT}, {self.PAYMENT_FORM}", timeout=self.wait_timeout
            )
            logger.info("✓ Payment page displayed")
            return True
        except PlaywrightTimeoutError:
            # Fallback: check URL
            if "reserve" in self.page.url.lower():
                logger.info("✓ Payment page detected via URL")
                return True
            logger.warning("Payment page not found within timeout")
            return False

    def fill_card_details(self, card_number: str, exp_month: str, exp_year: str, cvc: str):
        """
        Fill card details into Stripe Payment Element iframes

        Args:
            card_number: Card number (e.g. "4242424242424242")
            exp_month: Expiration month (e.g. "03")
            exp_year: Expiration year (e.g. "26")
            cvc: CVC code (e.g. "123")
        """
        logger.info("Filling card details into Stripe iframes")

        # Wait longer for Stripe to fully initialise
        self.page.wait_for_timeout(2000)
        self.page.wait_for_selector('iframe[name*="privateStripeFrame"]', timeout=self.wait_timeout)

        stripe_frames = self.page.locator('iframe[name*="privateStripeFrame"]')
        frame_count = stripe_frames.count()
        logger.info(f"Found {frame_count} Stripe iframe(s)")

        card_filled = exp_filled = cvc_filled = False

        for i in range(frame_count):
            frame_name = stripe_frames.nth(i).get_attribute("name")
            fc = self.page.frame_locator(f'iframe[name="{frame_name}"]')

            if not card_filled:
                inp = fc.locator('input[name="number"]')
                if inp.count() > 0:
                    # Wait for the input to be ready
                    inp.first.wait_for(state="visible", timeout=self.wait_timeout)
                    self.page.wait_for_timeout(500)  # Extra wait for Stripe to initialize field
                    # Click to focus the field
                    inp.first.click()
                    self.page.wait_for_timeout(300)
                    # Type with slower delay to ensure all digits are captured
                    inp.first.type(card_number, delay=100)
                    logger.info(f"✓ Card number filled: {card_number}")
                    card_filled = True

            if card_filled and not exp_filled:
                inp = fc.locator('input[name="expiry"]')
                if inp.count() > 0:
                    # Wait for the input to be ready
                    inp.first.wait_for(state="visible", timeout=self.wait_timeout)
                    self.page.wait_for_timeout(300)
                    inp.first.click()
                    self.page.wait_for_timeout(300)
                    inp.first.type(f"{exp_month}/{exp_year}", delay=100)
                    logger.info(f"✓ Expiry filled: {exp_month}/{exp_year}")
                    exp_filled = True

            if exp_filled and not cvc_filled:
                inp = fc.locator('input[name="cvc"]')
                if inp.count() > 0:
                    # Wait for the input to be ready
                    inp.first.wait_for(state="visible", timeout=self.wait_timeout)
                    self.page.wait_for_timeout(300)
                    inp.first.click()
                    self.page.wait_for_timeout(300)
                    inp.first.type(cvc, delay=100)
                    logger.info("✓ CVC filled")
                    cvc_filled = True

            if card_filled and exp_filled and cvc_filled:
                break

        if not (card_filled and exp_filled and cvc_filled):
            logger.error(
                f"Not all fields filled - card:{card_filled} exp:{exp_filled} cvc:{cvc_filled}"
            )
            raise Exception(f"Card details incomplete - card:{card_filled} exp:{exp_filled} cvc:{cvc_filled}")

    def fill_country(self, country: str) -> bool:
        """Select country from Stripe payment form"""
        logger.info(f"Filling country: {country}")
        try:
            self.page.wait_for_selector('iframe[name*="privateStripeFrame"]', timeout=self.wait_timeout)
            frames = self.page.locator('iframe[name*="privateStripeFrame"]')
            for i in range(frames.count()):
                frame_name = frames.nth(i).get_attribute("name")
                fc = self.page.frame_locator(f'iframe[name="{frame_name}"]')

                country_select = fc.locator('select[name*="country" i]')
                if country_select.count() > 0:
                    # Use label= to match display text (e.g. "United States"),
                    # not the internal option value (e.g. "US").
                    try:
                        country_select.first.select_option(label=country)
                    except Exception:
                        country_select.first.select_option(value=country)
                    logger.info(f"✓ Country selected: {country}")
                    return True

                country_input = fc.locator('input[name*="country" i]')
                if country_input.count() > 0:
                    country_input.first.type(country, delay=50)
                    logger.info(f"✓ Country filled: {country}")
                    return True

            logger.warning(f"Country field not found for: {country}")
            return False
        except Exception as e:
            logger.error(f"Error filling country: {e}")
            return False

    def fill_postal_code(self, postal_code: str) -> bool:
        """Fill postal code in Stripe payment form"""
        logger.info(f"Filling postal code: {postal_code}")
        try:
            frames = self.page.locator('iframe[name*="privateStripeFrame"]')
            for i in range(frames.count()):
                frame_name = frames.nth(i).get_attribute("name")
                fc = self.page.frame_locator(f'iframe[name="{frame_name}"]')

                inp = fc.locator('input[name="postalCode"]')
                if inp.count() > 0:
                    inp.first.type(postal_code, delay=50)
                    logger.info(f"✓ Postal code filled: {postal_code}")
                    return True

            logger.warning("Postal code field not found")
            return False
        except Exception as e:
            logger.error(f"Error filling postal code: {e}")
            return False

    def click_continue(self):
        """Click the Continue/Submit button for payment"""
        logger.info("Clicking Continue for payment")
        try:
            btn = self.page.locator(self.CONTINUE_BUTTON).first
            btn.wait_for(state="visible", timeout=5000)
            btn.click()
            logger.info("✓ Continue clicked")
            self.wait_for_navigation()
        except PlaywrightTimeoutError:
            logger.warning("Continue button not visible")
        except Exception as e:
            logger.error(f"Error clicking continue: {e}")
            raise


class QuestionnaireStartPage(BasePage):
    """Page object for questionnaire start page"""

    BEGIN_QUESTIONNAIRE_BUTTON = 'button:has-text("Begin Medical Questionnaire")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("QuestionnaireStartPage initialized")

    def is_questionnaire_start_displayed(self) -> bool:
        """Verify that questionnaire start page is displayed"""
        try:
            self.page.wait_for_selector(self.BEGIN_QUESTIONNAIRE_BUTTON, timeout=self.wait_timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def click_begin_questionnaire(self):
        """Click the 'Begin Medical Questionnaire' button"""
        logger.info("Clicking 'Begin Medical Questionnaire'")
        self.click(self.BEGIN_QUESTIONNAIRE_BUTTON)
        self.wait_for_navigation()


class GeneralQuestionnairePage(BasePage):
    """Page object for General Questionnaire page"""

    GENERAL_QUESTIONNAIRE_HEADER = ':has-text("General Questionnaire")'
    CONTINUE_BUTTON = 'button:has-text("Continue"), [role="button"]:has-text("Continue")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("GeneralQuestionnairePage initialized")

    def is_general_questionnaire_displayed(self) -> bool:
        """Check if General Questionnaire page is displayed"""
        return self.is_element_visible(self.GENERAL_QUESTIONNAIRE_HEADER)

    def click_continue(self):
        """Click Continue button"""
        self.click_when_enabled(self.CONTINUE_BUTTON)
        self.wait_for_navigation()


class ScanForYourselfPage(BasePage):
    """Page object for 'scan for yourself' selection page"""

    SCAN_FOR_YOURSELF_HEADER = ':has-text("scan for yourself")'
    MYSELF_OPTION = 'input[type="radio"], [role="radio"]'
    CONTINUE_BUTTON = 'button:has-text("Continue"), [role="button"]:has-text("Continue")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("ScanForYourselfPage initialized")

    def is_scan_for_yourself_displayed(self) -> bool:
        """Check if scan for yourself page is displayed"""
        return self.is_element_visible(self.SCAN_FOR_YOURSELF_HEADER)

    def select_myself(self):
        """Select the 'Myself' option"""
        logger.info("Selecting 'Myself' option")
        options = self.page.locator(self.MYSELF_OPTION)
        if options.count() > 0:
            options.first.click()
            logger.info("✓ 'Myself' selected")
        else:
            logger.warning("'Myself' option not found")

    def click_continue(self):
        """Click Continue"""
        self.click_when_enabled(self.CONTINUE_BUTTON, timeout=20000)
        self.wait_for_navigation()


class ReschedulingRefundPolicyPage(BasePage):
    """Page object for rescheduling and refund policy page"""

    RESCHEDULING_POLICY_HEADER = ':has-text("rescheduling and refund policy")'
    CONTINUE_BUTTON = 'button:has-text("Continue"), [role="button"]:has-text("Continue")'

    def __init__(self, page: Page, wait_timeout: int = 15000):
        super().__init__(page, wait_timeout)
        logger.info("ReschedulingRefundPolicyPage initialized")

    def is_rescheduling_policy_displayed(self) -> bool:
        """Check if rescheduling policy page is displayed"""
        return self.is_element_visible(self.RESCHEDULING_POLICY_HEADER)

    def click_continue(self):
        """Click the Continue button to proceed past the policy page."""
        logger.info("Clicking Continue on rescheduling/refund policy page")
        self.click_when_enabled(self.CONTINUE_BUTTON)
        self.wait_for_navigation()

