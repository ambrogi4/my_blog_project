from flask import Flask, render_template
import os
import markdown

app = Flask(__name__)
BLOG_POSTS_FOLDER = 'blog_posts'

# Ensure the blog posts folder exists
os.makedirs(BLOG_POSTS_FOLDER, exist_ok=True)

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

if __name__ == '__main__':
    app.run(debug=True)
