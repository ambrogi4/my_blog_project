from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import markdown
from models import User, BlogPost

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

def get_blog_posts(include_archived=False):
    """Get all blog posts, optionally including archived ones"""
    posts = []
    
    # Get active posts
    for filename in os.listdir(BLOG_POSTS_FOLDER):
        if filename.endswith('.md'):
            post = BlogPost.from_filename(filename)
            if post:
                posts.append(post)
    
    # Get archived posts if requested
    if include_archived:
        archived_dir = os.path.join(BLOG_POSTS_FOLDER, 'archived')
        if os.path.exists(archived_dir):
            for filename in os.listdir(archived_dir):
                if filename.endswith('.md'):
                    post = BlogPost.from_filename(f"archived/{filename}")
                    if post:
                        posts.append(post)
    
    return posts

def get_blog_post_content(filename):
    """Get blog post content by filename"""
    post = BlogPost.from_filename(filename)
    return post.content if post else None

@app.route('/')
def index():
    posts = get_blog_posts(include_archived=False)  # Only show active posts to public
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
    """Admin dashboard with all posts including archived"""
    posts = get_blog_posts(include_archived=True)
    return render_template('admin.html', posts=posts)

@app.route('/admin/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new blog post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            # Create filename from title
            filename = title.lower().replace(' ', '_').replace('-', '_') + '.md'
            
            # Check if file already exists
            if os.path.exists(os.path.join(BLOG_POSTS_FOLDER, filename)):
                flash('A post with this title already exists!', 'error')
                return render_template('edit_post.html', title=title, content=content)
            
            # Create and save the post
            post = BlogPost(filename, title, content)
            post.save()
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Title and content are required!', 'error')
    
    return render_template('edit_post.html', title='', content='')

@app.route('/admin/edit/<filename>', methods=['GET', 'POST'])
@login_required
def edit_post(filename):
    """Edit an existing blog post"""
    post = BlogPost.from_filename(filename)
    
    if not post:
        flash('Post not found!', 'error')
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            # Update the post
            post.title = title
            post.content = content
            
            # Handle filename change if title changed
            new_filename = title.lower().replace(' ', '_').replace('-', '_') + '.md'
            if new_filename != post.filename:
                # Check if new filename already exists
                if os.path.exists(os.path.join(BLOG_POSTS_FOLDER, new_filename)):
                    flash('A post with this title already exists!', 'error')
                    return render_template('edit_post.html', title=title, content=content, filename=filename)
                
                # Delete old file and update filename
                post.delete()
                post.filename = new_filename
            
            post.save()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Title and content are required!', 'error')
    
    return render_template('edit_post.html', title=post.title, content=post.content, filename=filename)

@app.route('/admin/archive/<filename>')
@login_required
def archive_post(filename):
    """Archive a blog post"""
    post = BlogPost.from_filename(filename)
    
    if not post:
        flash('Post not found!', 'error')
        return redirect(url_for('admin'))
    
    if post.is_archived:
        flash('Post is already archived!', 'error')
    else:
        post.archive()
        flash('Post archived successfully!', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/unarchive/<filename>')
@login_required
def unarchive_post(filename):
    """Unarchive a blog post"""
    post = BlogPost.from_filename(filename)
    
    if not post:
        flash('Post not found!', 'error')
        return redirect(url_for('admin'))
    
    if not post.is_archived:
        flash('Post is not archived!', 'error')
    else:
        post.unarchive()
        flash('Post unarchived successfully!', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<filename>')
@login_required
def delete_post(filename):
    """Delete a blog post"""
    post = BlogPost.from_filename(filename)
    
    if not post:
        flash('Post not found!', 'error')
        return redirect(url_for('admin'))
    
    if post.delete():
        flash('Post deleted successfully!', 'success')
    else:
        flash('Failed to delete post!', 'error')
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
