#!/usr/bin/env python3
"""
Script to fix WordPress format links in Hugo posts.
Converts sauvikbiswas.com/YYYY/MM/DD/post-slug/ to /posts/post-slug/
"""

import re
from pathlib import Path
from typing import List, Tuple

# Path to posts directory
POSTS_DIR = Path("content/posts")

# Pattern to match WordPress URLs
# Matches: http://sauvikbiswas.com/YYYY/MM/DD/post-slug/ or https://sauvikbiswas.com/YYYY/MM/DD/post-slug/
WORDPRESS_URL_PATTERN = re.compile(
    r'(https?://)?sauvikbiswas\.com/(\d{4})/(\d{2})/(\d{2})/([^/)\s"\'<>]+)/?',
    re.IGNORECASE
)


def extract_post_slug(url: str) -> str:
    """Extract the post slug from a WordPress URL."""
    match = WORDPRESS_URL_PATTERN.search(url)
    if match:
        return match.group(5)  # The post slug is the 5th group
    return None


def fix_wordpress_url(match: re.Match) -> str:
    """Replace WordPress URL with Hugo format."""
    post_slug = match.group(5)
    # Return relative Hugo URL
    return f"/posts/{post_slug}/"


def fix_links_in_content(content: str) -> Tuple[str, int]:
    """
    Fix WordPress links in markdown content.
    Returns: (updated_content, number_of_replacements)
    """
    replacements = 0
    
    def replace_wordpress_url(match: re.Match) -> str:
        """Replace a WordPress URL with Hugo format."""
        nonlocal replacements
        post_slug = match.group(5)  # Extract post slug
        replacements += 1
        return f"/posts/{post_slug}/"
    
    # Replace all WordPress URLs in the content
    # This will work for markdown links, HTML links, and standalone URLs
    content = WORDPRESS_URL_PATTERN.sub(replace_wordpress_url, content)
    
    return content, replacements


def process_post_file(post_file: Path) -> int:
    """Process a single post file and fix WordPress links."""
    try:
        content = post_file.read_text(encoding='utf-8')
        updated_content, replacements = fix_links_in_content(content)
        
        if replacements > 0:
            post_file.write_text(updated_content, encoding='utf-8')
            print(f"  Fixed {replacements} link(s) in {post_file.name}")
            return replacements
        return 0
    except Exception as e:
        print(f"  Error processing {post_file.name}: {e}")
        return 0


def main():
    """Main function to process all posts."""
    posts_dir = Path(POSTS_DIR)
    
    if not posts_dir.exists():
        print(f"Error: {posts_dir} does not exist")
        return
    
    # Find all index.md files in post directories
    post_files = list(posts_dir.glob("*/index.md"))
    
    print(f"Found {len(post_files)} post files")
    print(f"Scanning for WordPress links...\n")
    
    total_replacements = 0
    files_modified = 0
    
    for post_file in sorted(post_files):
        replacements = process_post_file(post_file)
        if replacements > 0:
            total_replacements += replacements
            files_modified += 1
    
    print(f"\nCompleted!")
    print(f"  Files modified: {files_modified}")
    print(f"  Total links fixed: {total_replacements}")


if __name__ == "__main__":
    main()

