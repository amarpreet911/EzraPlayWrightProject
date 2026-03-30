"""
Test: Signup New User and Book Appointment - Combined Flow
Tests the complete flow: new user signup -> immediate appointment booking

Test Flow:
- SIGNUP: Navigate to join -> Fill form -> Accept terms -> Submit -> Reach Select Plan
- BOOKING: DOB/Gender -> Select scan -> Select location -> Select date/time -> Payment

Run with: pytest tests/test_booking/test_signup_and_booking_new_user.py -v -s
"""

import pytest
import logging
from utils import UserDataManager
from pages import SignupPage, SelectPlanPage, ScanSelectionPage, LocationSelectionPage
from pages import DateTimeSelectionPage, PaymentPage
from config import BASE_URL

logger = logging.getLogger(__name__)


class TestSignupAndBookingNewUser:
    """Test suite for signup and booking flow with a new user"""

    def setup_method(self):
        """Setup before each test"""
        self.user_manager = UserDataManager()
        self.new_user = None

    @pytest.mark.signup
    @pytest.mark.booking
    def test_signup_new_user_and_book_appointment(self, page, payment_data):
        """
        Complete Signup and Appointment Booking for a New User

        Steps:
        1.  Generate new user from test_users.json configuration
        2.  Navigate to signup page
        3.  Fill signup form
        4.  Accept terms and conditions
        5.  Submit form
        6.  Verify successful signup (reach Select Plan page)
        7.  Fill Date of Birth and Gender
        8.  Select MRI scan
        9.  Select location
        10. Select date and time
        11. Fill payment details
        12. Submit payment
        13. Verify booking completion
        14. Save new user to test_users.json
        """
        # ── STEP 1: Generate New User ──────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: GENERATE NEW USER")
        logger.info("=" * 70)

        self.new_user = self.user_manager.generate_user_data()

        # Skip already-registered emails (max 5 attempts)
        for _ in range(5):
            existing_emails = [u["email"] for u in self.user_manager.data.get("users", [])]
            if self.new_user["email"] not in existing_emails:
                break
            logger.warning(f"Email {self.new_user['email']} already exists, incrementing...")
            self.user_manager.data["next_user_number"] += 1
            self.new_user = self.user_manager.generate_user_data()

        logger.info(f"✓ Generated: {self.new_user['first_name']} {self.new_user['last_name']}")
        logger.info(f"  Email: {self.new_user['email']}")

        # ── STEP 2: Navigate to Signup Page ───────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: NAVIGATE TO SIGNUP PAGE")
        logger.info("=" * 70)

        page.goto(f"{BASE_URL}/join", wait_until="domcontentloaded")
        logger.info(f"✓ Navigated to: {BASE_URL}/join")

        # ── STEP 3: Fill Signup Form ───────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: FILL SIGNUP FORM")
        logger.info("=" * 70)

        signup_page = SignupPage(page)
        assert signup_page.is_signup_page_displayed(), "Signup page not displayed"

        signup_page.fill_signup_form(
            first_name=self.new_user["first_name"],
            last_name=self.new_user["last_name"],
            email=self.new_user["email"],
            phone=self.new_user["phone"],
            password=self.new_user["password"],
        )
        logger.info("✓ Signup form filled")

        # ── STEP 4: Accept Terms ───────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: ACCEPT TERMS AND CONDITIONS")
        logger.info("=" * 70)

        signup_page.check_terms_agreement()
        logger.info("✓ Terms accepted")

        # ── STEP 5: Submit Form ────────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: SUBMIT SIGNUP FORM")
        logger.info("=" * 70)

        signup_page.submit_form()
        logger.info("✓ Form submitted — waiting for Select Plan page to load...")

        # ── STEP 6: Verify Signup Success ─────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 6: VERIFY SIGNUP SUCCESS")
        logger.info("=" * 70)

        # Wait for the URL to actually change to the select-plan page (up to 30s)
        confirmed = signup_page.wait_for_signup_confirmation(max_wait=30)
        assert confirmed, f"Signup failed — did not reach select-plan page. URL: {page.url}"

        # Also wait for page content (DOB field or scan cards) to be visible
        page.wait_for_selector(
            'input[id="dob"], input[name="dob"], input[placeholder*="date" i], .multiselect',
            timeout=30000
        )
        current_url = page.url
        logger.info(f"✅ Signup successful — URL: {current_url}")

        # ── STEP 7: Save New User to test_users.json ──────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 7: SAVE NEW USER TO test_users.json")
        logger.info("=" * 70)

        # Save the newly created user to the JSON file for future tests
        self.user_manager.add_user(self.new_user)
        logger.info(f"✓ User {self.new_user['id']} saved to test_users.json")
        logger.info(f"✓ Next user number will be: {self.user_manager.data.get('next_user_number')}")

        # ── STEP 8: Fill DOB and Gender ────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 8: FILL DATE OF BIRTH AND GENDER")
        logger.info("=" * 70)

        select_plan = SelectPlanPage(page)

        if select_plan.is_select_plan_page_displayed():
            logger.info("✓ Select Plan page is displayed")
            
            # Fill DOB and gender only — do NOT click Continue here.
            # The Continue button is disabled until an MRI scan card is selected (Step 9).
            success = select_plan.select_gender_and_dob()
            
            if success:
                logger.info("✓ DOB and Gender filled successfully")
                # Wait for form to settle before scan selection
                page.wait_for_timeout(1000)
            else:
                logger.warning("⚠️ Failed to fill DOB and Gender, but continuing anyway")
        else:
            logger.info("⚠️ Select Plan page not clearly detected — proceeding to scan selection")

        # ── STEP 9: Select MRI Scan ────────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 9: SELECT MRI SCAN")
        logger.info("=" * 70)

        # We are still on the select-plan page — DOB/Gender + MRI card are all on the same page.
        # Selecting the MRI card will enable the Continue button.
        scan_selection = ScanSelectionPage(page)
        logger.info("Checking if scan selection page is displayed...")
        assert scan_selection.is_scan_selection_displayed(), "Scan selection page not found"
        
        logger.info("✓ Scan selection page found, selecting MRI...")
        scan_selection.select_mri_scan()
        
        logger.info("✓ MRI Scan selected, clicking continue...")
        scan_selection.click_continue()
        logger.info("✓ MRI Scan selected and continued")
        
        # Wait for page to navigate to location selection
        page.wait_for_timeout(2500)

        # ── STEP 10: Select Location ────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 10: SELECT LOCATION")
        logger.info("=" * 70)

        # Wait for page to be ready
        page.wait_for_timeout(1000)

        location = LocationSelectionPage(page)
        logger.info("Checking if location selection page is displayed...")
        assert location.is_location_selection_displayed(), "Location selection page not found"
        
        logger.info("✓ Location selection page found, selecting recommended...")
        location.select_recommended_location()
        logger.info("✓ Recommended location selected")
        
        # Wait for page to navigate to date/time selection
        page.wait_for_timeout(2500)

        # ── STEP 11: Select Date and Time ─────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 11: SELECT DATE AND TIME")
        logger.info("=" * 70)

        # Wait for page to be ready
        page.wait_for_timeout(1000)

        date_time = DateTimeSelectionPage(page)
        logger.info("Checking if date/time selection page is displayed...")
        assert date_time.is_date_time_selection_displayed(), "Date/time selection page not found"
        
        logger.info("✓ Date/time selection page found, selecting date...")
        date_time.select_first_available_date()
        logger.info("✓ Date selected, selecting time...")
        date_time.select_first_available_time()
        logger.info("✓ Time selected, clicking continue...")
        date_time.click_continue()
        logger.info("✓ Date and time selected")

        # ── STEP 12: Fill Payment Details ─────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 12: FILL PAYMENT DETAILS")
        logger.info("=" * 70)

        payment_page = PaymentPage(page)
        assert payment_page.is_payment_page_displayed(), "Payment page not found"

        payment_page.fill_card_details(
            card_number=payment_data["card_number"],
            exp_month=payment_data["expiry_month"],
            exp_year=payment_data["expiry_year"],
            cvc=payment_data["cvc"],
        )
        payment_page.fill_country(payment_data["country"])
        payment_page.fill_postal_code(payment_data["postal_code"])
        logger.info("✓ Payment details filled")

        # ── STEP 13: Submit Payment ────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 13: SUBMIT PAYMENT")
        logger.info("=" * 70)

        submit_btn = page.locator('[data-test="submit"]')
        assert submit_btn.count() > 0, "Submit button not found"
        submit_btn.first.click()
        page.wait_for_timeout(5000)
        logger.info("✓ Payment submitted")

        # ── STEP 14: Verify Booking Completion ────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 14: VERIFY BOOKING COMPLETION")
        logger.info("=" * 70)

        page.wait_for_timeout(3000)
        current_url = page.url
        assert any(kw in current_url for kw in ["book-scan", "reserve", "appointment", "scan-confirm"]), (
            f"Booking not confirmed — unexpected URL: {current_url}"
        )

        page.screenshot(path="tests/test_booking/signup_and_booking_completed.png")
        logger.info(f"✓ Booking confirmed — URL: {current_url}")


        logger.info("\n" + "=" * 70)
        logger.info("✅ TEST PASSED — SIGNUP AND BOOKING COMPLETED!")
        logger.info("=" * 70)
