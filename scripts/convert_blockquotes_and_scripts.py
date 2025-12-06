#!/usr/bin/env python3
"""
Convert HTML blockquote and script tags to Hugo shortcode/markdown format.

Converts:
- Twitter blockquotes to Hugo shortcode format ({{< twitter >}})
- Regular blockquotes to markdown format (> quote)
- Script tags to Hugo shortcode format
"""

import re
import os
from pathlib import Path


def convert_twitter_blockquote_to_shortcode(content):
    """Convert Twitter blockquotes to Hugo shortcode format."""
    
    # Pattern to match Twitter blockquote tags
    pattern = r'<blockquote\s+class=["\']twitter-tweet["\'][^>]*>(.*?)</blockquote>'
    
    def replace_twitter_blockquote(match):
        blockquote_tag = match.group(0)
        inner_html = match.group(1)
        
        # Extract attributes
        cards = None
        lang = None
        conversation = None
        
        # Extract data-cards
        cards_match = re.search(r'data-cards=["\']([^"\']+)["\']', blockquote_tag, re.IGNORECASE)
        if cards_match:
            cards = cards_match.group(1)
        
        # Extract data-lang
        lang_match = re.search(r'data-lang=["\']([^"\']+)["\']', blockquote_tag, re.IGNORECASE)
        if lang_match:
            lang = lang_match.group(1)
        
        # Extract data-conversation
        conversation_match = re.search(r'data-conversation=["\']([^"\']+)["\']', blockquote_tag, re.IGNORECASE)
        if conversation_match:
            conversation = conversation_match.group(1)
        
        # Extract tweet URL from inner HTML
        tweet_url_match = re.search(r'href=["\'](https://twitter\.com/[^"\']+/status/[^"\']+)["\']', inner_html, re.IGNORECASE)
        tweet_url = None
        if tweet_url_match:
            tweet_url = tweet_url_match.group(1)
        
        # Extract tweet text (from paragraph)
        tweet_text_match = re.search(r'<p[^>]*>(.*?)</p>', inner_html, re.DOTALL | re.IGNORECASE)
        tweet_text = None
        if tweet_text_match:
            tweet_text = tweet_text_match.group(1)
            # Remove HTML tags from tweet text
            tweet_text = re.sub(r'<[^>]+>', '', tweet_text)
            tweet_text = tweet_text.strip()
            # Escape quotes for shortcode
            tweet_text = tweet_text.replace('"', '\\"')
        
        # Extract author and date
        author_date_match = re.search(r'—\s*([^<]+)\s*<a[^>]*>([^<]+)</a>', inner_html, re.IGNORECASE)
        author = None
        date = None
        if author_date_match:
            author = author_date_match.group(1).strip()
            date = author_date_match.group(2).strip()
            # Escape quotes for shortcode
            author = author.replace('"', '\\"')
            date = date.replace('"', '\\"')
        
        # Build shortcode
        shortcode_parts = []
        
        if tweet_url:
            shortcode_parts.append(f'url="{tweet_url}"')
        if cards:
            shortcode_parts.append(f'cards="{cards}"')
        if lang:
            shortcode_parts.append(f'lang="{lang}"')
        if conversation:
            shortcode_parts.append(f'conversation="{conversation}"')
        if tweet_text:
            shortcode_parts.append(f'text="{tweet_text}"')
        if author:
            shortcode_parts.append(f'author="{author}"')
        if date:
            shortcode_parts.append(f'date="{date}"')
        
        # Use a self-closing shortcode with all parameters
        shortcode = '{{< twitter ' + ' '.join(shortcode_parts) + ' >}}'
        
        return shortcode
    
    # Replace all occurrences with DOTALL flag to match across newlines
    converted = re.sub(pattern, replace_twitter_blockquote, content, flags=re.DOTALL | re.IGNORECASE)
    
    return converted


def convert_blockquote_to_markdown(content):
    """Convert regular blockquotes (non-Twitter) to markdown format."""
    
    # Pattern to match blockquote tags that are NOT Twitter embeds
    # Twitter blockquotes have class="twitter-tweet" or similar
    pattern = r'<blockquote(?![^>]*class=["\']twitter[^"\']*["\'])[^>]*>(.*?)</blockquote>'
    
    def replace_blockquote(match):
        quote_content = match.group(1).strip()
        
        # Remove HTML tags from quote content (keep text)
        # This is a simple approach - remove common HTML tags
        quote_content = re.sub(r'<[^>]+>', '', quote_content)
        
        # Clean up whitespace
        quote_content = ' '.join(quote_content.split())
        
        # Convert to markdown blockquote format
        # Each line should start with >
        lines = quote_content.split('\n')
        markdown_lines = []
        for line in lines:
            line = line.strip()
            if line:
                markdown_lines.append(f'> {line}')
            else:
                markdown_lines.append('>')
        
        return '\n'.join(markdown_lines) if markdown_lines else '> ' + quote_content
    
    # Replace all occurrences with DOTALL flag to match across newlines
    converted = re.sub(pattern, replace_blockquote, content, flags=re.DOTALL | re.IGNORECASE)
    
    return converted


def convert_script_to_shortcode(content):
    """Convert script tags to Hugo shortcode format."""
    
    # Pattern to match script tags (handles single-line and multi-line)
    # \s* allows for optional whitespace, \s+ requires at least one space or attribute
    pattern = r'<script\s+([^>]*?)></script>'
    
    def replace_script(match):
        attributes = match.group(1)
        
        # Parse attributes
        src = None
        async_attr = False
        defer_attr = False
        charset = None
        
        # Extract src
        src_match = re.search(r'src\s*=\s*["\']([^"\']+)["\']', attributes, re.IGNORECASE)
        if src_match:
            src = src_match.group(1)
        
        # Check for async
        if re.search(r'\basync\b', attributes, re.IGNORECASE):
            async_attr = True
        
        # Check for defer
        if re.search(r'\bdefer\b', attributes, re.IGNORECASE):
            defer_attr = True
        
        # Extract charset
        charset_match = re.search(r'charset\s*=\s*["\']([^"\']+)["\']', attributes, re.IGNORECASE)
        if charset_match:
            charset = charset_match.group(1)
        
        # Build shortcode
        shortcode_parts = []
        
        if src:
            shortcode_parts.append(f'src="{src}"')
        if async_attr:
            shortcode_parts.append('async="true"')
        if defer_attr:
            shortcode_parts.append('defer="true"')
        if charset:
            shortcode_parts.append(f'charset="{charset}"')
        
        shortcode = '{{< script ' + ' '.join(shortcode_parts) + ' >}}'
        return shortcode
    
    # Replace all occurrences with DOTALL to handle multi-line tags
    converted = re.sub(pattern, replace_script, content, flags=re.IGNORECASE | re.DOTALL)
    
    return converted


def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Convert Twitter blockquotes first (before regular blockquotes)
        content = convert_twitter_blockquote_to_shortcode(content)
        
        # Convert regular blockquotes to markdown
        content = convert_blockquote_to_markdown(content)
        
        # Then convert scripts
        content = convert_script_to_shortcode(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
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

