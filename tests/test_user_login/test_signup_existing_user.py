"""
Test 3: Signup with EXISTING Email - Error Handling
Tests the scenario where a user tries to signup with an already registered email

SUCCESS CRITERIA:
✓ Error message appears: "If you have previously created an account try logging in instead."
✓ User stays on signup page (no navigation to Select Plan page)
✓ Form should NOT be submitted
"""

import pytest
import logging
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from config import BASE_URL

logger = logging.getLogger(__name__)


class TestSignupWithExistingUserEmail:
    """Test suite for signup error handling when using an existing user's email"""
    
    @pytest.mark.signup
    def test_signup_attempt_with_existing_user_email(self, page, existing_user):
        """
        Test Case: Signup Attempt with Existing User Email
        
        Verifies that the application properly rejects signup attempts 
        when using an email that already belongs to a registered user.
        
        Test Flow:
        1. Navigate to login page
        2. Click 'Join' button to go to signup page
        3. Fill signup form with ALREADY REGISTERED email (first user from test_users.json)
        4. Fill other fields with new data
        5. Check 'I agree to terms' checkbox
        6. Submit the form
        7. Verify error message appears: "If you have previously created an account try logging in instead."
        8. Verify we stay on signup page (no navigation away)
        
        Args:
            page: Playwright page fixture
            existing_user: First registered user loaded from fixtures/test_users.json
        """
        # All fields loaded dynamically from test_users.json — no hardcoding
        existing_user_email = existing_user["email"]
        new_first_name     = existing_user["first_name"]
        new_last_name      = existing_user["last_name"]
        new_phone          = existing_user["phone"]
        new_password       = existing_user["password"]
        
        # ============================================================
        # Step 1: Navigate to Login Page
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 1: NAVIGATE TO LOGIN PAGE")
        logger.info("="*70)
        
        login_page = LoginPage(page, wait_timeout=15000)
        login_page.navigate_to(BASE_URL)
        
        assert login_page.is_login_page_displayed(), \
            "Login page should be displayed"
        
        logger.info("✓ Login page displayed")
        
        # ============================================================
        # Step 2: Click Join Button
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 2: CLICK JOIN BUTTON")
        logger.info("="*70)
        
        login_page.click_join_button()
        logger.info("✓ Join button clicked, navigating to signup page")
        
        # Wait for page to load after navigation
        page.wait_for_timeout(2000)
        
        # ============================================================
        # Step 3: Fill Signup Form with EXISTING USER EMAIL
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 3: FILL SIGNUP FORM WITH EXISTING USER EMAIL")
        logger.info("="*70)
        
        signup_page = SignupPage(page, wait_timeout=15000)
        
        assert signup_page.is_signup_page_displayed(), \
            "Signup page should be displayed after clicking Join"
        
        logger.info("✓ Signup page displayed")
        
        logger.info(f"Using EXISTING USER email: {existing_user_email}")
        logger.info(f"Filling form with: {new_first_name} {new_last_name}")
        
        signup_page.fill_signup_form(
            first_name=new_first_name,
            last_name=new_last_name,
            email=existing_user_email,  # ← Using already registered email
            phone=new_phone,
            password=new_password
        )
        
        logger.info("✓ Signup form fields filled (with existing user email)")
        
        # ============================================================
        # Step 4: Check Terms Agreement
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 4: CHECK TERMS AGREEMENT")
        logger.info("="*70)
        
        signup_page.check_terms_agreement()
        logger.info("✓ Terms agreement checkbox checked")
        
        # ============================================================
        # Step 5: Submit Form
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 5: SUBMIT FORM WITH EXISTING USER EMAIL")
        logger.info("="*70)
        
        success = signup_page.submit_form()
        assert success, "Form submission should attempt"
        
        logger.info("✓ Form submitted")
        
        # ============================================================
        # Step 6: Verify Error Message Appears
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 6: VERIFY EXISTING USER EMAIL ERROR MESSAGE")
        logger.info("="*70)
        
        # Wait and check for error message
        error_detected = signup_page.wait_for_duplicate_email_error(max_wait=10)
        
        current_url = page.url
        logger.info(f"Current URL: {current_url}")
        
        if error_detected:
            logger.info("✓ ✓ ✓ SUCCESS! DUPLICATE EMAIL ERROR MESSAGE APPEARED")
            logger.info("✓ Error message: 'If you have previously created an account try logging in instead.'")
        else:
            logger.warning("⚠️ ERROR MESSAGE NOT DETECTED")
            logger.warning(f"⚠️ Current URL: {current_url}")
            logger.info("ℹ️ Expected: Error message about existing account")
        
        # ============================================================
        # Step 7: Verify We're Still on Signup Page
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 7: VERIFY STILL ON SIGNUP PAGE (NO NAVIGATION)")
        logger.info("="*70)
        
        still_on_signup = "/join" in current_url or signup_page.is_signup_page_displayed()
        
        if still_on_signup:
            logger.info("✓ Still on signup page (form was not submitted)")
            logger.info("✓ Correct behavior: Form should not be submitted with duplicate email")
        else:
            logger.warning("⚠️ UNEXPECTED: Navigated away from signup page")
            logger.warning(f"⚠️ Current URL: {current_url}")
        
        # Save final page screenshot
        screenshot_path = "screenshots/duplicate_email_error.png"
        page.screenshot(path=screenshot_path)
        logger.info(f"✓ Saved final page screenshot: {screenshot_path}")
        
        # ============================================================
        # TEST COMPLETED SUCCESSFULLY
        # ============================================================
        logger.info("\n" + "="*70)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"✓ Existing user email signup error handling test passed")
        logger.info(f"✓ Email used: {existing_user_email}")
        logger.info(f"✓ Error message displayed: {error_detected}")
        logger.info(f"✓ Still on signup page: {still_on_signup}")
        logger.info("="*70)
        
        # Assert that both conditions are met
        assert error_detected, "Existing user email error message should be displayed"
        assert still_on_signup, "Should remain on signup page when using existing user email"

