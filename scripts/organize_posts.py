#!/usr/bin/env python3
"""
Script to organize posts from export/output/posts into content/posts
Each post gets its own folder with the markdown file and referenced images.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Set, List, Dict

# Paths
EXPORT_POSTS_DIR = Path("export/output/posts")
EXPORT_IMAGES_DIR = Path("export/output/posts/images")
CONTENT_POSTS_DIR = Path("content/posts")

# Image extensions to look for
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}


def extract_frontmatter(content: str) -> tuple:
    """Extract frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_text = parts[1]
    body = parts[2]
    
    # Parse frontmatter for coverImage (simple regex-based parsing)
    frontmatter = {}
    cover_match = re.search(r'coverImage:\s*["\']?([^"\'\n]+)["\']?', frontmatter_text)
    if cover_match:
        frontmatter['coverImage'] = cover_match.group(1).strip('"\'')
    
    return frontmatter, body


def find_image_references(content: str) -> Set[str]:
    """Find all image references in markdown content."""
    images = set()
    
    # Find markdown image syntax: ![](images/filename.jpg) or ![alt](images/filename.jpg)
    pattern = r'!\[.*?\]\(([^)]+\.(?:jpg|jpeg|png|gif|webp|svg))\)'
    matches = re.findall(pattern, content, re.IGNORECASE)
    for match in matches:
        # Remove "images/" prefix if present
        img_path = match.replace('images/', '').strip()
        images.add(img_path)
    
    return images


def find_cover_image(frontmatter: dict) -> Set[str]:
    """Extract coverImage from frontmatter."""
    images = set()
    if 'coverImage' in frontmatter:
        img = frontmatter['coverImage']
        if img:
            # Remove quotes if present
            img = img.strip('"\'')
            images.add(img)
    return images


def find_image_file(image_name: str, images_dir: Path) -> Path:
    """Find the actual image file, handling variations in naming."""
    # Try exact match first
    exact_path = images_dir / image_name
    if exact_path.exists():
        return exact_path
    
    # Try without "images/" prefix if it was included
    if image_name.startswith('images/'):
        image_name = image_name[7:]
    
    exact_path = images_dir / image_name
    if exact_path.exists():
        return exact_path
    
    # Try case-insensitive match
    image_lower = image_name.lower()
    for img_file in images_dir.iterdir():
        if img_file.name.lower() == image_lower:
            return img_file
    
    # Try partial match (for cases like "filename-1024x768.jpg" vs "filename.jpg")
    base_name = Path(image_name).stem
    base_lower = base_name.lower()
    
    # Remove size suffixes like "-1024x768"
    base_clean = re.sub(r'-\d+x\d+$', '', base_lower)
    
    for img_file in images_dir.iterdir():
        img_stem = img_file.stem.lower()
        img_clean = re.sub(r'-\d+x\d+$', '', img_stem)
        
        if base_clean == img_clean:
            return img_file
    
    return None


def update_image_paths(content: str) -> str:
    """Update image paths in markdown to remove 'images/' prefix."""
    # Replace ![](images/filename.jpg) with ![](filename.jpg)
    pattern = r'!\[([^\]]*)\]\(images/([^)]+)\)'
    content = re.sub(pattern, r'![\1](\2)', content)
    return content


def process_post(post_file: Path, images_dir: Path, output_dir: Path):
    """Process a single post file."""
    post_name = post_file.stem  # filename without .md extension
    post_folder = output_dir / post_name
    
    # Create post folder
    post_folder.mkdir(parents=True, exist_ok=True)
    
    # Read post content
    content = post_file.read_text(encoding='utf-8')
    
    # Extract frontmatter and body
    frontmatter, body = extract_frontmatter(content)
    
    # Find all image references
    images = set()
    images.update(find_image_references(body))
    images.update(find_cover_image(frontmatter))
    
    # Copy images
    copied_images = {}
    for img_name in images:
        img_path = find_image_file(img_name, images_dir)
        if img_path and img_path.exists():
            dest_path = post_folder / img_path.name
            shutil.copy2(img_path, dest_path)
            copied_images[img_name] = img_path.name
            print(f"  Copied image: {img_path.name}")
        else:
            print(f"  Warning: Image not found: {img_name}")
    
    # Update image paths in content
    body = update_image_paths(body)
    
    # Update coverImage path if it exists
    updated_cover_image = None
    if 'coverImage' in frontmatter and frontmatter['coverImage']:
        cover_img = frontmatter['coverImage'].strip('"\'')
        if cover_img in copied_images:
            updated_cover_image = copied_images[cover_img]
    
    # Reconstruct content with updated frontmatter
    original_parts = content.split('---', 2)
    if len(original_parts) >= 3:
        # Has frontmatter
        frontmatter_text = original_parts[1]
        if updated_cover_image:
            # Replace coverImage value in frontmatter
            frontmatter_text = re.sub(
                r'coverImage:\s*["\']?[^"\'\n]+["\']?',
                f'coverImage: "{updated_cover_image}"',
                frontmatter_text
            )
        updated_content = "---" + frontmatter_text + "---" + body
    else:
        # No frontmatter
        updated_content = body
    
    # Write updated markdown as index.md
    output_file = post_folder / "index.md"
    output_file.write_text(updated_content, encoding='utf-8')
    
    return len(copied_images)


def main():
    """Main function to process all posts."""
    export_posts = Path(EXPORT_POSTS_DIR)
    export_images = Path(EXPORT_IMAGES_DIR)
    content_posts = Path(CONTENT_POSTS_DIR)
    
    # Verify directories exist
    if not export_posts.exists():
        print(f"Error: {export_posts} does not exist")
        return
    
    if not export_images.exists():
        print(f"Error: {export_images} does not exist")
        return
    
    # Create output directory
    content_posts.mkdir(parents=True, exist_ok=True)
    
    # Find all markdown files
    markdown_files = list(export_posts.glob("*.md"))
    
    print(f"Found {len(markdown_files)} post files")
    print(f"Processing posts from {export_posts} to {content_posts}\n")
    
    total_images = 0
    for post_file in sorted(markdown_files):
        print(f"Processing: {post_file.name}")
        img_count = process_post(post_file, export_images, content_posts)
        total_images += img_count
        print(f"  Done ({img_count} images)\n")
    
    print(f"Completed! Processed {len(markdown_files)} posts with {total_images} total image copies.")


if __name__ == "__main__":
    main()

