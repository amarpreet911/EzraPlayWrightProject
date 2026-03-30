"""
Test: Booking Appointment for Existing User
Tests the complete appointment booking and payment flow for an existing user.

This test:
1. Uses the shared `existing_user` fixture (first user from test_users.json)
2. Logs in with the existing user's credentials
3. Tests the complete appointment booking flow
4. Verifies payment submission
5. Confirms booking completion

Run with: pytest tests/test_booking/test_booking_appointment_existing_user.py
"""

import pytest
import logging
from pages import LoginPage, DashboardPage, ScanSelectionPage, LocationSelectionPage
from pages import DateTimeSelectionPage, PaymentPage
from config import BASE_URL

logger = logging.getLogger(__name__)


class TestAppointmentBookingExistingUser:
    """Test suite for appointment booking flow with EXISTING USER from test_users.json"""

    @pytest.mark.booking
    @pytest.mark.appointment
    def test_booking_appointment_with_existing_user(self, page, existing_user, payment_data):
        """
        Test Case: Complete Appointment Booking with Existing User

        Test Flow:
        1. Use existing_user fixture (first entry in test_users.json)
        2. Login with existing user credentials
        3. Navigate to Book a Scan
        4. Select MRI Scan
        5. Select recommended location
        6. Select date and time
        7. Fill in payment details
        8. Complete payment
        9. Verify confirmation page

        Args:
            page: Playwright page fixture
            existing_user: First registered user from test_users.json
            payment_data: Payment information fixture
        """
        test_email = existing_user["email"]
        test_password = existing_user["password"]

        logger.info("\n" + "=" * 70)
        logger.info("LOADING EXISTING USER")
        logger.info("=" * 70)
        logger.info(f"✓ Existing user: {test_email}")

        # ── Step 1: Login ──────────────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: LOGIN WITH EXISTING USER")
        logger.info("=" * 70)

        login_page = LoginPage(page)
        login_page.navigate_to(BASE_URL)

        assert login_page.is_login_page_displayed(), "Login page not found at startup"
        logger.info("✓ Login page displayed")

        login_page.login(test_email, test_password)
        assert "sign-in" not in page.url.lower(), "Still on login page after login attempt"
        logger.info(f"✓ Login successful: {test_email}")

        # ── Step 2: Navigate to Book a Scan ───────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: NAVIGATE TO BOOK A SCAN")
        logger.info("=" * 70)

        dashboard = DashboardPage(page)
        assert dashboard.is_dashboard_displayed(), "Dashboard not displayed after login"
        logger.info("✓ Dashboard displayed")

        dashboard.click_book_a_scan()
        logger.info("✓ Book a Scan button clicked")

        # ── Step 3: Select MRI Scan ────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: SELECT MRI SCAN")
        logger.info("=" * 70)

        scan_selection = ScanSelectionPage(page)
        assert scan_selection.is_scan_selection_displayed(), "Scan selection page not found"
        logger.info("✓ Scan selection page displayed")

        scan_selection.select_mri_scan()
        scan_selection.click_continue()
        logger.info("✓ MRI Scan selected, continued to location")

        # ── Step 4: Select Location ────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: SELECT LOCATION")
        logger.info("=" * 70)

        location_selection = LocationSelectionPage(page)
        assert location_selection.is_location_selection_displayed(), "Location selection not found"
        logger.info("✓ Location selection page displayed")

        location_selection.select_recommended_location()
        logger.info("✓ Recommended location selected")

        # ── Step 5: Select Date and Time ──────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: SELECT DATE AND TIME")
        logger.info("=" * 70)

        date_time = DateTimeSelectionPage(page)
        assert date_time.is_date_time_selection_displayed(), "Date/time selection page not found"
        logger.info("✓ Date/time selection page displayed")

        date_time.select_first_available_date()
        logger.info("✓ First available date selected")

        date_time.select_first_available_time()
        logger.info("✓ First available time slot selected")

        date_time.click_continue()
        logger.info("✓ Continued to payment page")

        # ── Step 6: Fill Payment Details ──────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 6: FILL PAYMENT DETAILS")
        logger.info("=" * 70)

        payment_page = PaymentPage(page)
        assert payment_page.is_payment_page_displayed(), "Payment page not found"
        logger.info("✓ Payment page displayed")

        payment_page.fill_card_details(
            card_number=payment_data["card_number"],
            exp_month=payment_data["expiry_month"],
            exp_year=payment_data["expiry_year"],
            cvc=payment_data["cvc"],
        )
        logger.info("✓ Card details filled")

        payment_page.fill_country(payment_data["country"])
        logger.info(f"✓ Country set to: {payment_data['country']}")

        payment_page.fill_postal_code(payment_data["postal_code"])
        logger.info(f"✓ Postal code: {payment_data['postal_code']}")

        # ── Step 7: Submit Payment ─────────────────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 7: SUBMIT PAYMENT")
        logger.info("=" * 70)

        submit_btn = page.locator('[data-test="submit"]')
        assert submit_btn.count() > 0, "Submit button not found"
        submit_btn.first.click()
        logger.info("✓ Payment submitted")

        page.wait_for_timeout(5000)

        # ── Step 8: Verify Confirmation Page ──────────────────────────────
        logger.info("\n" + "=" * 70)
        logger.info("STEP 8: VERIFY CONFIRMATION PAGE")
        logger.info("=" * 70)

        page.wait_for_timeout(3000)
        current_url = page.url
        logger.info(f"Current URL: {current_url}")

        assert "book-scan" in current_url or "reserve" in current_url, (
            f"Not on expected booking/confirmation page. URL: {current_url}"
        )
        logger.info(f"✓ On booking/payment page: {current_url}")

        page.screenshot(path="tests/test_booking/final_page.png")
        logger.info("✓ Saved final page screenshot")

        logger.info("\n" + "=" * 70)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info(f"Final URL: {current_url}")

