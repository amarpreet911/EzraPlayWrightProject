"""
DOB and Gender Selection Helpers
Utility functions for Date of Birth and Gender selection testing
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def generate_random_dob(start_year: int = 1910, end_year: int = 1990) -> str:
    """
    Generate a random date of birth between start_year and end_year
    Returns in MM-DD-YYYY format
    
    Args:
        start_year: Start year (default 1910)
        end_year: End year (default 1990)
        
    Returns:
        Date string in MM-DD-YYYY format
    """
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    random_date = start_date + timedelta(days=random_days)
    dob_string = random_date.strftime("%m-%d-%Y")
    logger.info(f"Generated random DOB: {dob_string}")
    return dob_string


def select_random_gender() -> str:
    """
    Select random gender value (Male or Female)
    
    Returns:
        str: "Male" or "Female"
    """
    gender = random.choice(["Male", "Female"])
    logger.info(f"Selected random gender: {gender}")
    return gender


def generate_test_user_dob_gender() -> dict:
    """
    Generate random DOB and Gender for test user
    
    Returns:
        dict: {"dob": "MM-DD-YYYY", "gender": "Male" or "Female"}
    """
    dob = generate_random_dob()
    gender = select_random_gender()
    return {"dob": dob, "gender": gender}

