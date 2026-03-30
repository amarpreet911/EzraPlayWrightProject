"""
Test: New User Signup Flow
Verifies a new user can complete the signup process and reach the Select Plan page.

Run with: pytest tests/test_user_login/test_signup_new_user.py -v -s
"""

import pytest
import logging
from utils.user_data_manager import UserDataManager
from pages.signup_page import SignupPage
from config import BASE_URL

logger = logging.getLogger(__name__)


class TestNewUserSignup:
    """Test suite for new user signup flow"""

    def setup_method(self):
        """Setup before each test"""
        self.user_manager = UserDataManager()
        self.new_user = None

    @pytest.mark.signup
    def test_new_user_signup(self, page):
        """
        Verify a new user can sign up successfully and reach the Select Plan page.

        Steps:
        1. Generate a new user from test_users.json configuration
        2. Navigate to the signup page
        3. Fill the signup form
        4. Accept terms and conditions
        5. Submit the form
        6. Verify the user reaches the Select Plan page

        Args:
            page: Playwright page fixture
        """
        # ============================================================
        # STEP 1: Generate New User
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 1: GENERATE NEW USER")
        logger.info("=" * 70)

        self.new_user = self.user_manager.generate_user_data()

        # Skip already-registered emails (max 5 attempts)
        for _ in range(5):
            existing_emails = [u["email"] for u in self.user_manager.data.get("users", [])]
            if self.new_user["email"] not in existing_emails:
                break
            logger.warning(f"Email {self.new_user['email']} already exists, trying next...")
            self.user_manager.data["next_user_number"] += 1
            self.new_user = self.user_manager.generate_user_data()

        logger.info(f"✓ Generated user: {self.new_user['first_name']} {self.new_user['last_name']}")
        logger.info(f"  Email: {self.new_user['email']}")

        # ============================================================
        # STEP 2: Navigate to Signup Page
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 2: NAVIGATE TO SIGNUP PAGE")
        logger.info("=" * 70)

        page.goto(f"{BASE_URL}/join", wait_until="domcontentloaded")
        logger.info(f"✓ Navigated to: {BASE_URL}/join")

        # ============================================================
        # STEP 3: Fill Signup Form
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 3: FILL SIGNUP FORM")
        logger.info("=" * 70)

        signup_page = SignupPage(page, wait_timeout=15000)
        assert signup_page.is_signup_page_displayed(), "Signup page not displayed"

        signup_page.fill_signup_form(
            first_name=self.new_user["first_name"],
            last_name=self.new_user["last_name"],
            email=self.new_user["email"],
            phone=self.new_user["phone"],
            password=self.new_user["password"],
        )
        logger.info("✓ Signup form filled")

        # ============================================================
        # STEP 4: Accept Terms and Conditions
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 4: ACCEPT TERMS AND CONDITIONS")
        logger.info("=" * 70)

        signup_page.check_terms_agreement()
        logger.info("✓ Terms accepted")
        
        # Wait for form to settle after checking terms
        page.wait_for_timeout(1500)

        # ============================================================
        # STEP 5: Submit Signup Form
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 5: SUBMIT SIGNUP FORM")
        logger.info("=" * 70)

        signup_page.submit_form()
        logger.info("✓ Form submitted — waiting for Select Plan page to load...")

        # ============================================================
        # STEP 6: Verify Signup Success (Select Plan page reached)
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 6: VERIFY SIGNUP SUCCESS")
        logger.info("=" * 70)

        # Wait for the URL to actually change to the select-plan page (up to 30s)
        confirmed = signup_page.wait_for_signup_confirmation(max_wait=30)
        assert confirmed, f"Signup failed — did not reach select-plan page. URL: {page.url}"

        # Also wait for page content (DOB field) to be visible before proceeding
        page.wait_for_selector(
            'input[id="dob"], input[name="dob"], input[placeholder*="date" i], .multiselect',
            timeout=30000
        )
        current_url = page.url
        logger.info(f"✅ Signup successful — URL: {current_url}")
        logger.info("=" * 70)
        
        # ============================================================
        # STEP 7: Save New User to test_users.json
        # ============================================================
        logger.info("\n" + "=" * 70)
        logger.info("STEP 7: SAVE NEW USER TO test_users.json")
        logger.info("=" * 70)
        
        # Save the newly created user to the JSON file for future tests
        self.user_manager.add_user(self.new_user)
        logger.info(f"✓ User {self.new_user['id']} saved to test_users.json")
        logger.info(f"✓ Next user number will be: {self.user_manager.data.get('next_user_number')}")
