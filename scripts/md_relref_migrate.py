#!/usr/bin/env python3
"""
Convert hardcoded /posts/slug/ markdown links to Hugo relref shortcodes.

Skips bundle asset URLs (/posts/slug/image.jpg). Use --dry-run to preview.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CONTENT_DIR = Path("content")
ASSET_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".mp4", ".mov",
}

# [text](/posts/slug/) or [text](/posts/slug "title")
PAGE_LINK_RE = re.compile(
    r'\]\((/posts/[^)\s"]+?)/?(?:\s+"([^"]*)")?\)'
)


def load_hugo_slugs() -> set[str]:
    try:
        out = subprocess.check_output(["hugo", "list", "all"], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Warning: could not run hugo list all ({exc}); slug validation disabled")
        return set()

    slugs: set[str] = set()
    for line in out.strip().splitlines():
        path = line.split(",", 1)[0]
        match = re.match(r"content/posts/([^/]+)/", path)
        if match:
            slugs.add(match.group(1))
    return slugs


def is_asset_path(url_path: str) -> bool:
    path = url_path.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    parts = path.split("/")
    # /posts/slug/asset.ext -> 4+ parts
    if len(parts) > 3:
        return True
    if len(parts) == 3:
        return Path(parts[2]).suffix.lower() in ASSET_EXTENSIONS
    return False


def extract_slug(url_path: str) -> str | None:
    path = url_path.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    parts = path.split("/")
    if len(parts) != 3 or parts[1] != "posts":
        return None
    return parts[2]


def inside_double_quoted_attribute(text: str, pos: int) -> bool:
    """True if pos lies inside a double-quoted shortcode/HTML attribute value."""
    i = pos - 1
    while i >= 0:
        if text[i] == '"':
            j = i - 1
            while j >= 0 and text[j] in " \t":
                j -= 1
            if j >= 0 and text[j] == "=":
                return True
            return False
        i -= 1
    return False


def relref_shortcode(slug: str, escaped: bool) -> str:
    if escaped:
        return f'{{{{< relref \\"posts/{slug}\\" >}}}}'
    return f'{{{{< relref "posts/{slug}" >}}}}'


def migrate_content(text: str, known_slugs: set[str]) -> tuple[str, list[str], list[str]]:
    changes: list[str] = []
    broken: list[str] = []

    def replacer(match: re.Match[str]) -> str:
        url_path = match.group(1)
        title = match.group(2)

        if "relref" in url_path:
            return match.group(0)
        if is_asset_path(url_path):
            return match.group(0)

        slug = extract_slug(url_path)
        if slug is None:
            return match.group(0)

        if known_slugs and slug not in known_slugs:
            broken.append(slug)
            return match.group(0)

        escaped = inside_double_quoted_attribute(text, match.start())
        shortcode = relref_shortcode(slug, escaped)
        title_suffix = f' "{title}"' if title else ""
        changes.append(slug)
        return f"]({shortcode}{title_suffix})"

    new_text = PAGE_LINK_RE.sub(replacer, text)
    return new_text, changes, broken


def iter_markdown_files(root: Path):
    yield from sorted(root.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write converted files",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")

    known_slugs = load_hugo_slugs()
    total_changes = 0
    files_changed = 0
    all_broken: set[str] = set()

    for md_file in iter_markdown_files(CONTENT_DIR):
        original = md_file.read_text(encoding="utf-8")
        updated, changes, broken = migrate_content(original, known_slugs)
        all_broken.update(broken)

        if not changes:
            continue

        files_changed += 1
        total_changes += len(changes)
        rel = md_file.as_posix()
        print(f"{rel}: {len(changes)} link(s)")
        for slug in changes:
            print(f"  -> posts/{slug}")

        if args.apply:
            md_file.write_text(updated, encoding="utf-8")

    print()
    print(f"Files: {files_changed}, conversions: {total_changes}")
    if all_broken:
        print(f"Skipped broken targets ({len(all_broken)}):")
        for slug in sorted(all_broken):
            print(f"  posts/{slug}")
        return 1

    if args.dry_run:
        print("(dry run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
