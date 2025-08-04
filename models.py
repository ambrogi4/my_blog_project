from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

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

class BlogPost:
    def __init__(self, filename, title, content, created_date=None, is_archived=False):
        self.filename = filename
        self.title = title
        self.content = content
        self.created_date = created_date or datetime.now()
        self.is_archived = is_archived
    
    @staticmethod
    def from_filename(filename, blog_posts_folder='blog_posts', archived_folder='blog_posts/archived'):
        """Create a BlogPost object from a filename"""
        if filename.startswith('archived/'):
            filepath = os.path.join(blog_posts_folder, filename)
            is_archived = True
        else:
            filepath = os.path.join(blog_posts_folder, filename)
            is_archived = False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from filename
            title = filename.replace('.md', '').replace('_', ' ').title()
            if filename.startswith('archived/'):
                title = filename.replace('archived/', '').replace('.md', '').replace('_', ' ').title()
            
            return BlogPost(filename, title, content, is_archived=is_archived)
        except FileNotFoundError:
            return None
    
    def save(self, blog_posts_folder='blog_posts'):
        """Save the blog post to file"""
        if self.is_archived:
            # Ensure archived directory exists
            archived_dir = os.path.join(blog_posts_folder, 'archived')
            os.makedirs(archived_dir, exist_ok=True)
            filepath = os.path.join(archived_dir, self.filename.replace('archived/', ''))
        else:
            filepath = os.path.join(blog_posts_folder, self.filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def archive(self, blog_posts_folder='blog_posts'):
        """Archive the blog post"""
        if not self.is_archived:
            # Move from main folder to archived folder
            old_path = os.path.join(blog_posts_folder, self.filename)
            archived_dir = os.path.join(blog_posts_folder, 'archived')
            os.makedirs(archived_dir, exist_ok=True)
            new_path = os.path.join(archived_dir, self.filename)
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                self.filename = f"archived/{self.filename}"
                self.is_archived = True
    
    def unarchive(self, blog_posts_folder='blog_posts'):
        """Unarchive the blog post"""
        if self.is_archived:
            # Move from archived folder to main folder
            old_path = os.path.join(blog_posts_folder, self.filename)
            new_path = os.path.join(blog_posts_folder, self.filename.replace('archived/', ''))
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                self.filename = self.filename.replace('archived/', '')
                self.is_archived = False
    
    def delete(self, blog_posts_folder='blog_posts'):
        """Delete the blog post file"""
        if self.is_archived:
            filepath = os.path.join(blog_posts_folder, self.filename)
        else:
            filepath = os.path.join(blog_posts_folder, self.filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False 