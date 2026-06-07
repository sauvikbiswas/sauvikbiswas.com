#!/usr/bin/env python3
"""Rename day-* post folders to {trip-tag-yyyy}-day-{padded-day}-{desc}."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_POSTS = ROOT / "content" / "posts"
STATIC_POSTS = ROOT / "static" / "posts"
CONTENT_DIR = ROOT / "content"
REPORT_PATH = ROOT / "reports" / "day-post-rename-map.csv"

TRIP_TAG_MAP = {
    "north-east-trip-14": "north-east-trip-2014",
    "himachal-trip-15": "himachal-trip-2015",
    "kerala-trip-15": "kerala-trip-2015",
    "vietnam-trip-15": "vietnam-trip-2015",
    "kodaikanal-ooty-trip-16": "kodaikanal-ooty-trip-2016",
    "tour-of-nilgiris-16": "tour-of-nilgiris-2016",
    "mangalore-udupi-trip-17": "mangalore-udupi-trip-2017",
    "uttarakhand-trip-17": "uttarakhand-trip-2017",
    "europe-trip-19": "europe-trip-2018",
    "himachal-trip-19": "himachal-trip-2019",
    "north-east-trip-20": "north-east-trip-2020",
}

TRIP_TAG_PATTERN = re.compile(
    r"(\s+- )\"(" + "|".join(re.escape(k) for k in TRIP_TAG_MAP) + r")\""
)
DAY_SLUG_PATTERN = re.compile(r"^day-(\d+(?:-\d+)*)-(.+)$")
OLD_SLUG_FROM_PATH = re.compile(r"posts/(day-[0-9][^\s\"'>]*)")


def read_trip_tag(index_path: Path) -> tuple[str, str]:
    text = index_path.read_text(encoding="utf-8")
    for old_tag, new_tag in TRIP_TAG_MAP.items():
        if f'"{new_tag}"' in text:
            return old_tag, new_tag
    for old_tag, new_tag in TRIP_TAG_MAP.items():
        if f'"{old_tag}"' in text:
            return old_tag, new_tag
    raise ValueError(f"No trip tag found in {index_path}")


def pad_day_segment(day_part: str) -> str:
    return "-".join(f"{int(n):02d}" for n in day_part.split("-"))


def new_slug_from_old(old_slug: str, trip_prefix: str) -> str:
    match = DAY_SLUG_PATTERN.match(old_slug)
    if not match:
        raise ValueError(f"Unexpected slug format: {old_slug}")
    day_part = match.group(1)
    desc = match.group(2)
    padded = pad_day_segment(day_part)
    return f"{trip_prefix}-day-{padded}-{desc}"


def all_old_slugs() -> list[str]:
    slugs = {p.name for p in CONTENT_POSTS.glob("day-*") if p.is_dir()}
    proc = subprocess.run(
        ["git", "ls-files", "--stage", "content/posts/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        path = parts[1]
        if path.startswith("content/posts/day-") and path.endswith("/index.md"):
            slugs.add(Path(path).parent.name)
    return sorted(slugs)



def build_mapping() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_new: set[str] = set()
    for old_slug in all_old_slugs():
        index_path = CONTENT_POSTS / old_slug / "index.md"
        if index_path.exists():
            old_tag, new_tag = read_trip_tag(index_path)
            new_slug = new_slug_from_old(old_slug, new_tag)
        else:
            match = DAY_SLUG_PATTERN.match(old_slug)
            if not match:
                raise ValueError(f"Unexpected slug format: {old_slug}")
            desc = match.group(2)
            matches = [
                p
                for p in CONTENT_POSTS.glob("*-day-*")
                if p.is_dir() and p.name.endswith(desc)
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"Could not resolve renamed slug for {old_slug}: {matches}"
                )
            new_slug = matches[0].name
            old_tag, new_tag = read_trip_tag(matches[0] / "index.md")
        if new_slug in seen_new:
            continue
        seen_new.add(new_slug)
        rows.append(
            {
                "old_slug": old_slug,
                "new_slug": new_slug,
                "old_tag": old_tag,
                "new_tag": new_tag,
            }
        )
    return rows


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["old_slug", "new_slug", "old_tag", "new_tag"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {REPORT_PATH}")


def update_front_matter_tag(index_path: Path, old_tag: str, new_tag: str) -> None:
    text = index_path.read_text(encoding="utf-8")
    if f'"{new_tag}"' in text:
        return
    updated, count = TRIP_TAG_PATTERN.subn(rf'\1"{new_tag}"', text, count=1)
    if count != 1:
        raise ValueError(f"Expected one tag replacement in {index_path}, got {count}")
    index_path.write_text(updated, encoding="utf-8")


def git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, check=True)


def rename_folders(rows: list[dict[str, str]]) -> None:
    for row in rows:
        old_slug = row["old_slug"]
        new_slug = row["new_slug"]
        content_src = CONTENT_POSTS / old_slug
        content_dst = CONTENT_POSTS / new_slug
        if content_src.exists():
            git_mv(content_src, content_dst)
        static_src = STATIC_POSTS / old_slug
        static_dst = STATIC_POSTS / new_slug
        if static_src.exists():
            static_dst.parent.mkdir(parents=True, exist_ok=True)
            if static_dst.exists():
                raise FileExistsError(static_dst)
            shutil.move(str(static_src), str(static_dst))


def replace_references(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda r: len(r["old_slug"]), reverse=True)
    md_files = list(CONTENT_DIR.rglob("*.md"))
    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        original = text
        for row in ordered:
            old_slug = row["old_slug"]
            new_slug = row["new_slug"]
            text = text.replace(f"posts/{old_slug}", f"posts/{new_slug}")
        if text != original:
            md_file.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform renames and content updates (default: mapping only)",
    )
    args = parser.parse_args()

    rows = build_mapping()
    write_report(rows)

    duplicates = {r["new_slug"] for r in rows}
    if len(duplicates) != len(rows):
        raise SystemExit("Duplicate new slugs detected")

    if not args.apply:
        print("Dry run complete. Re-run with --apply to execute.")
        return

    # Tags first while paths still use old folder names during rename batch.
    for row in rows:
        content_src = CONTENT_POSTS / row["old_slug"] / "index.md"
        if content_src.exists():
            update_front_matter_tag(content_src, row["old_tag"], row["new_tag"])

    rename_folders(rows)
    replace_references(rows)
    print(f"Renamed {len(rows)} post bundles and updated content references.")


if __name__ == "__main__":
    main()
