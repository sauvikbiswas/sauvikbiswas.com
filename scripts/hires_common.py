"""Shared helpers for hires_image_audit.py and hires_md_apply_links.py."""

from __future__ import annotations

import os
import re

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

RESIZE_SUFFIX = re.compile(r"^(.*)-(\d+)x(\d+)$", re.IGNORECASE)

# Shortcode: non-greedy body without `>` before closing (matches audit scanner).
FIGURE_SRC = re.compile(
    r"\{\{<\s*figure\s+[^>]*?src\s*=\s*[\"']([^\"']+)[\"'][^>]*>\}\}",
    re.IGNORECASE | re.DOTALL,
)


def strip_last_resize_suffix(filename: str) -> str:
    stem, ext = os.path.splitext(filename)
    m = RESIZE_SUFFIX.match(stem)
    if m:
        return m.group(1) + ext
    return filename


def strip_all_resize_suffixes(filename: str) -> str:
    """WordPress may stack multiple intermediate sizes (e.g. -1200x800-768x432.jpg)."""
    cur = filename
    while True:
        nxt = strip_last_resize_suffix(cur)
        if nxt == cur:
            return cur
        cur = nxt


def is_resized_basename(name: str) -> bool:
    stem, ext = os.path.splitext(name)
    if ext.lower() not in IMG_EXT:
        return False
    if stem.lower().endswith("-scaled"):
        return False
    return bool(RESIZE_SUFFIX.match(stem))
