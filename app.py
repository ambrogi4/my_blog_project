from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import markdown
from models import User

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!
BLOG_POSTS_FOLDER = 'blog_posts'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure the blog posts folder exists
os.makedirs(BLOG_POSTS_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    if user_id == '1':  # Simple check for our single user
        return User.get_user()
    return None

def get_blog_posts():
    posts = []
    for filename in os.listdir(BLOG_POSTS_FOLDER):
        if filename.endswith('.md'):
            # For simplicity, we'll just store the filename for now
            posts.append({'filename': filename})
    return posts

def get_blog_post_content(filename):
    filepath = os.path.join(BLOG_POSTS_FOLDER, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    posts = get_blog_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<filename>')
def view_post(filename):
    content = get_blog_post_content(filename)
    if content:
        # Convert Markdown to HTML
        html_content = markdown.markdown(content)
        return render_template('post.html', content=html_content)
    else:
        return 'Post not found'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_user()
        
        if user and user.username == username and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard - placeholder for future admin features"""
    posts = get_blog_posts()
    return render_template('admin.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
