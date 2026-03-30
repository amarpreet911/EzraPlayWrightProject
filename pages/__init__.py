"""
Pages package for Ezra Booking Tests
Contains all page object models
"""

from .base_page import BasePage
from .login_page import LoginPage
from .signup_page import SignupPage
from .select_plan_page import SelectPlanPage
from .booking_pages import DashboardPage, ScanSelectionPage, LocationSelectionPage
from .date_time_page import DateTimeSelectionPage
from .questionnaire_pages import (
    PaymentPage,
    QuestionnaireStartPage,
    GeneralQuestionnairePage,
    ScanForYourselfPage,
    ReschedulingRefundPolicyPage,
)

__all__ = [
    "BasePage",
    "LoginPage",
    "SignupPage",
    "SelectPlanPage",
    "DashboardPage",
    "ScanSelectionPage",
    "LocationSelectionPage",
    "DateTimeSelectionPage",
    "PaymentPage",
    "QuestionnaireStartPage",
    "GeneralQuestionnairePage",
    "ScanForYourselfPage",
    "ReschedulingRefundPolicyPage",
]

