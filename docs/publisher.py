#!/usr/bin/env python3
"""Blog publisher — manages posts, RSS feed, and static site generation."""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
BLOG_DIR = BASE_DIR / "blog"
POSTS_DIR = BLOG_DIR / "posts"
CSS_DIR = BLOG_DIR / "css"

# Ensure directories exist
POSTS_DIR.mkdir(parents=True, exist_ok=True)
CSS_DIR.mkdir(parent_ok=True)


def create_post(title: str, slug: str, content: str, tags: list = None):
    """Create a new blog post."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Fair Dinkum Publishing</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a href="/" class="logo">🇦🇺 <span>Fair Dinkum</span> Publishing</a>
            <nav>
                <a href="/">Home</a>
                <a href="/about.html">About</a>
                <a href="/rss.xml">RSS</a>
            </nav>
        </div>
    </header>

    <main class="container">
        <article class="post-article">
            <h1>{title}</h1>
            <time datetime="{today}">{datetime.now().strftime("%B %d, %Y")}</time>
            {content}
        </article>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>© 2026 Fair Dinkum Publishing · ABN 63 590 716 023 · Adelaide SA</p>
        </div>
    </footer>
</body>
</html>"""
    
    post_path = POSTS_DIR / f"{slug}.html"
    post_path.write_text(html)
    print(f"Created: {post_path}")


def rebuild_index():
    """Rebuild index.html from existing posts."""
    pass


def rebuild_rss():
    """Rebuild rss.xml from existing posts."""
    pass


if __name__ == "__main__":
    pass
