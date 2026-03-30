"""
User Data Management Module
Manages test user generation and data persistence
"""

import json
import os
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UserDataManager:
    """Manages test user data and generation"""

    def __init__(self, json_file_path: str = None):
        """
        Initialize UserDataManager
        
        Args:
            json_file_path: Path to test_users.json file
        """
        if json_file_path is None:
            # Default to fixtures directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(
                os.path.dirname(current_dir), 
                "fixtures", 
                "test_users.json"
            )
        
        self.json_file_path = json_file_path
        self.data = self._load_data()
        logger.info(f"UserDataManager initialized with file: {self.json_file_path}")

    def _load_data(self) -> Dict:
        """Load user data from JSON file"""
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"User data file not found: {self.json_file_path}")
        
        with open(self.json_file_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded user data with {len(data.get('users', []))} users")
        return data

    def _save_data(self):
        """Save user data to JSON file"""
        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
        
        with open(self.json_file_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        logger.info("User data saved to JSON file")

    def get_next_user_number(self) -> int:
        """Get the next user number to use"""
        return self.data.get("next_user_number", 2)

    def generate_user_data(self) -> Dict:
        """
        Generate new user data based on the pattern in JSON file
        
        Returns:
            dict: New user data with incremented number
        """
        next_number = self.get_next_user_number()
        base_config = self.data.get("base_config", {})
        
        # Build password using the wildcard pattern
        password_suffix = base_config.get('password_suffix', '426*')
        if '*' in password_suffix:
            # Replace * with the user ID number
            password_suffix = password_suffix.replace('*', str(next_number))
        
        # Generate new user data
        new_user = {
            "id": next_number,
            "first_name": f"{base_config.get('first_name_prefix', 'Preet')}{next_number}",
            "last_name": f"{base_config.get('last_name_prefix', 'Test')}{next_number}",
            "email": f"{base_config.get('email_base', 'amarpreet911+')}{next_number}{base_config.get('email_domain', '@gmail.com')}",
            "phone": base_config.get("phone", "1111111111"),
            "password": f"{base_config.get('password_prefix', 'TestPreet@')}{password_suffix}",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Generated user data for user #{next_number}")
        logger.info(f"  - Name: {new_user['first_name']} {new_user['last_name']}")
        logger.info(f"  - Email: {new_user['email']}")
        
        return new_user

    def add_user(self, user_data: Dict = None) -> Dict:
        """
        Add a new user to the JSON file
        
        Args:
            user_data: Optional user data dict. If None, generates new data.
        
        Returns:
            dict: The added user data
        """
        if user_data is None:
            user_data = self.generate_user_data()
        
        # Add to users list
        self.data["users"].append(user_data)
        
        # Increment next user number
        next_number = user_data.get("id", 2) + 1
        self.data["next_user_number"] = next_number
        
        # Save to file
        self._save_data()
        
        logger.info(f"✓ User added successfully. Next user number will be: {next_number}")
        
        return user_data

    def get_latest_user(self) -> Dict:
        """Get the latest user from the file"""
        users = self.data.get("users", [])
        if users:
            return users[-1]
        return None

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.data.get("users", [])

    def get_user_by_email(self, email: str) -> Dict:
        """Get user by email address"""
        users = self.data.get("users", [])
        for user in users:
            if user.get("email") == email:
                return user
        return None

