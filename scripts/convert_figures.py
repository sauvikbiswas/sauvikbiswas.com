#!/usr/bin/env python3
"""
Convert HTML figure tags to Hugo shortcode format.

Converts:
<figure>
[![](IMAGE.jpg)](URL)
<figcaption>
CAPTION
</figcaption>
</figure>

To:
{{< figure src="IMAGE.jpg" caption="CAPTION" >}}
"""

import re
import os
from pathlib import Path


def convert_figure_to_shortcode(content):
    """Convert figure tags to Hugo shortcode format."""
    
    # Pattern to match the entire figure block
    # Handles multiple cases:
    # 1. [![](image.jpg)](url) - with link, no alt text
    # 2. [![alt text](image.jpg)](url) - with link, with alt text
    # 3. ![](image.jpg) - without link, no alt text
    # 4. ![alt text](image.jpg) - without link, with alt text
    # Uses DOTALL flag to match across newlines and handle blank lines
    pattern = r'<figure>\s*\n\s*(?:\[!\[([^\]]*)\]\(([^)]+)\)\]\([^)]+\)|!\[([^\]]*)\]\(([^)]+)\))\s*\n\s*<figcaption>\s*\n\s*(.*?)\s*\n\s*</figcaption>\s*\n\s*</figure>'
    
    def replace_figure(match):
        # Get image name from either:
        # - group 2 (with link, image path) or group 4 (without link, image path)
        # Groups 1 and 3 are alt text (which we ignore)
        image_name = match.group(2) or match.group(4)
        caption = match.group(5).strip()
        
        # Clean up caption - remove extra whitespace/newlines but preserve single spaces
        caption = ' '.join(caption.split())
        
        # Escape quotes in caption for Hugo shortcode
        caption = caption.replace('"', '\\"')
        
        # Return Hugo shortcode format
        return f'{{{{< figure src="{image_name}" caption="{caption}" >}}}}'
    
    # Replace all occurrences with DOTALL flag to match across newlines
    converted = re.sub(pattern, replace_figure, content, flags=re.DOTALL | re.MULTILINE)
    
    return converted


def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        converted = convert_figure_to_shortcode(content)
        
        # Only write if content changed
        if converted != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all markdown files in posts directory."""
    posts_dir = Path(__file__).parent.parent / 'content' / 'posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    converted_count = 0
    processed_count = 0
    
    # Find all index.md files in post directories
    for md_file in posts_dir.rglob('index.md'):
        processed_count += 1
        if process_file(md_file):
            converted_count += 1
            print(f"Converted: {md_file.relative_to(posts_dir.parent.parent)}")
    
    print(f"\nProcessed {processed_count} files, converted {converted_count} files.")


if __name__ == '__main__':
    main()

