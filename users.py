# users.py
import os
import json
import hashlib
import datetime
from pathlib import Path

class UserManager:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.users_file = self.data_dir / "users.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create users file if it doesn't exist
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def hash_password(self, password):
        """Hash a password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_timestamp(self):
        """Get current timestamp in ISO format"""
        return datetime.datetime.now().isoformat()
    
    def create_user(self, username, password, first_name, last_name, email, student_id, visa_status, program):
        """Create a new user"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            users = {}
        
        if username in users:
            return False, "Username already exists"
        
        users[username] = {
            "username": username,
            "password": self.hash_password(password),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "student_id": student_id,
            "visa_status": visa_status,
            "program": program,
            "created_at": self.get_timestamp(),
            "last_login": self.get_timestamp()
        }
        
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True, "User created successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            users = {}
        
        if username not in users:
            return False, "Invalid username or password"
        
        if users[username]["password"] != self.hash_password(password):
            return False, "Invalid username or password"
        
        # Update last login time
        users[username]["last_login"] = self.get_timestamp()
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        # Return user info without password
        user_info = users[username].copy()
        user_info.pop("password")
        return True, user_info
    
    def get_user(self, username):
        """Get user information"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            users = {}
        
        if username not in users:
            return None
        
        # Return user info without password
        user_info = users[username].copy()
        user_info.pop("password")
        return user_info