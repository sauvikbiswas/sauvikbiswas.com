#!/usr/bin/env python3
"""
Convert HTML iframe tags to Hugo shortcode format.

Converts:
<iframe src="URL" width="W" height="H" ...></iframe>
or
<iframe src="URL" style="width: W; height: H; ..."></iframe>

To:
{{< iframe "URL" "W" "H" >}}
"""

import re
import os
from pathlib import Path


def extract_style_value(style_str, property_name):
    """Extract a CSS property value from a style string."""
    if not style_str:
        return None
    
    # Pattern to match "property: value;" or "property: value" (at end)
    pattern = rf'{property_name}\s*:\s*([^;]+)'
    match = re.search(pattern, style_str, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        # Remove quotes if present
        value = value.strip('"\'')
        return value
    return None


def parse_iframe_attributes(iframe_tag):
    """Parse iframe tag and extract src, width, and height."""
    src = None
    width = None
    height = None
    
    # Extract src attribute
    src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', iframe_tag, re.IGNORECASE)
    if src_match:
        src = src_match.group(1)
    
    # Extract width attribute
    width_match = re.search(r'width\s*=\s*["\']([^"\']+)["\']', iframe_tag, re.IGNORECASE)
    if width_match:
        width = width_match.group(1)
    
    # Extract height attribute
    height_match = re.search(r'height\s*=\s*["\']([^"\']+)["\']', iframe_tag, re.IGNORECASE)
    if height_match:
        height = height_match.group(1)
    
    # If width/height not found in attributes, check style attribute
    style_match = re.search(r'style\s*=\s*["\']([^"\']+)["\']', iframe_tag, re.IGNORECASE)
    if style_match:
        style_str = style_match.group(1)
        if not width:
            width = extract_style_value(style_str, 'width')
        if not height:
            height = extract_style_value(style_str, 'height')
        
        # If width is very small (like "1px"), prefer min-width if available
        if width and (width == '1px' or width == '0px'):
            min_width = extract_style_value(style_str, 'min-width')
            if min_width:
                width = min_width
        
        # If height is very small, prefer min-height if available
        if height and (height == '1px' or height == '0px'):
            min_height = extract_style_value(style_str, 'min-height')
            if min_height:
                height = min_height
    
    return src, width, height


def convert_iframe_to_shortcode(content):
    """Convert iframe tags to Hugo shortcode format."""
    
    # Pattern to match iframe tags (handles self-closing and regular closing tags)
    # Uses DOTALL flag to match across newlines if needed
    pattern = r'<iframe[^>]*>.*?</iframe>'
    
    def replace_iframe(match):
        iframe_tag = match.group(0)
        src, width, height = parse_iframe_attributes(iframe_tag)
        
        if not src:
            # If no src found, return original
            return iframe_tag
        
        # Build shortcode
        shortcode_parts = [f'"{src}"']
        
        if width:
            # Clean up width value (remove units like px, %, etc. if needed, or keep as is)
            width_clean = width.strip()
            shortcode_parts.append(f'"{width_clean}"')
        
        if height:
            # Clean up height value
            height_clean = height.strip()
            # Only add height if width was also provided (Hugo shortcode expects positional args)
            if width:
                shortcode_parts.append(f'"{height_clean}"')
            else:
                # If no width but height exists, add empty width first
                shortcode_parts.append('""')
                shortcode_parts.append(f'"{height_clean}"')
        
        shortcode = '{{< iframe ' + ' '.join(shortcode_parts) + ' >}}'
        return shortcode
    
    # Replace all occurrences
    converted = re.sub(pattern, replace_iframe, content, flags=re.DOTALL | re.IGNORECASE)
    
    return converted


def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        converted = convert_iframe_to_shortcode(content)
        
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

