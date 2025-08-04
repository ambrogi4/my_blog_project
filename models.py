from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash
    
    @staticmethod
    def create_user(username, password):
        """Create a new user with hashed password"""
        password_hash = generate_password_hash(password)
        return User(1, username, password_hash)  # Simple ID for single user
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_user():
        """Get the single admin user (for simplicity, we'll use a single user)"""
        # In a real app, you'd load this from a database
        # For now, we'll create a default admin user
        return User(1, 'admin', generate_password_hash('admin123')) 