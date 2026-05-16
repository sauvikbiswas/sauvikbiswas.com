#!/usr/bin/env python3
"""
Hi-res image audit: index WordPress uploads from sauvikbiswas.ls.log, scan Hugo
content for resized images, emit JSON/CSV/summary/extract script.

Usage:
  python3 scripts/hires_image_audit.py              # write reports only
  python3 scripts/hires_image_audit.py --apply      # extract from tar + copy to static/
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import shutil
import sys
import tarfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import unquote

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from hires_common import (  # noqa: E402
    FIGURE_SRC,
    IMG_EXT,
    RESIZE_SUFFIX,
    is_resized_basename,
    strip_all_resize_suffixes,
)

# --- constants (relative to repo root) ---
ARCHIVE_TARBALL_REL = Path("sauvikbiswas/sauvikbiswas.tar.gz")
LS_LOG_REL = Path("sauvikbiswas/sauvikbiswas.ls.log")
UPLOADS_MARKER = "wp/wp-content/uploads/"
ARCHIVE_MEMBER_PREFIX = "var/www/html/sauvikbiswas/wp/wp-content/uploads/"

WP_UPLOADS_URL = re.compile(
    r"https?://(?:www\.)?sauvikbiswas\.com/wp-content/uploads/(\d{4})/(\d{2})/([^?#]+)",
    re.IGNORECASE,
)
# Any host wp-content/uploads
WP_UPLOADS_URL_ANY = re.compile(
    r"https?://[^/]+/wp-content/uploads/(\d{4})/(\d{2})/([^?#]+)", re.IGNORECASE
)

LS_LINE_PATH = re.compile(
    r"\s+(\d+)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+"
    r"(var/www/html/sauvikbiswas/wp/wp-content/uploads/\S+)$"
)

DATE_LINE = re.compile(r"^date:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def repo_root() -> Path:
    p = Path(__file__).resolve().parent.parent
    if (p / "hugo.toml").is_file():
        return p
    raise SystemExit("Run from sauvikbiswas.com repo (hugo.toml not found)")


def classify_upload_basename(basename: str) -> str:
    stem, ext = os.path.splitext(basename)
    if ext.lower() not in IMG_EXT:
        return "other"
    if stem.lower().endswith("-scaled"):
        return "scaled"
    if RESIZE_SUFFIX.match(stem):
        return "resized"
    return "full"


def parse_ls_log(log_path: Path) -> tuple[dict[tuple[str, str, str], list[dict]], dict[str, list[tuple[str, str, str]]]]:
    """
    Returns:
      index_by_key: (yyyy, mm, basename) -> [{path, size, kind}, ...]
      basename_index: basename -> [(yyyy, mm, basename), ...]
    """
    index_by_key: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    basename_index: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    with log_path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if UPLOADS_MARKER not in line:
                continue
            m = LS_LINE_PATH.search(line)
            if not m:
                # Fallback: path from last occurrence of var/www
                idx = line.find("var/www/html/sauvikbiswas/wp/wp-content/uploads/")
                if idx < 0:
                    continue
                member = line[idx:].strip()
                size_m = re.search(r"\s(\d+)\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+", line)
                size = int(size_m.group(1)) if size_m else 0
            else:
                size = int(m.group(1))
                member = m.group(2)

            if not any(member.lower().endswith(ext) for ext in IMG_EXT):
                continue

            parts = member.split("/")
            try:
                uidx = parts.index("uploads")
                yyyy, mm = parts[uidx + 1], parts[uidx + 2]
            except (ValueError, IndexError):
                continue

            basename = parts[-1]
            kind = classify_upload_basename(basename)
            key = (yyyy, mm, basename)
            rec = {"path": member, "size": size, "kind": kind}
            index_by_key[key].append(rec)
            basename_index[basename].append((yyyy, mm, basename))

    return index_by_key, basename_index


def parse_front_matter_date(md_text: str) -> tuple[str, str] | None:
    if not md_text.startswith("---"):
        return None
    end = md_text.find("\n---", 3)
    if end < 0:
        return None
    fm = md_text[3:end]
    dm = DATE_LINE.search(fm)
    if not dm:
        return None
    raw = dm.group(1).strip().strip('"').strip("'")
    # 2019-11-06 or 2019-11-06T12:00:00Z
    m = re.match(r"(\d{4})-(\d{2})-\d{2}", raw)
    if m:
        return m.group(1), m.group(2)
    return None


def content_dest_relpath(md_path: Path, content_root: Path) -> str:
    rel = md_path.relative_to(content_root)
    parts = rel.parts
    if parts[-1] == "index.md":
        return str(Path(*parts[:-1])) if len(parts) > 1 else ""
    return str(Path(parts[0], Path(rel).stem))


def public_url_from_dest(dest_relpath: str, basename: str) -> str:
    p = dest_relpath.strip("/").replace("\\", "/")
    if not p:
        return "/" + basename
    return "/" + p + "/" + basename


def archive_source_dir(yyyy: str, mm: str) -> str:
    return f"{ARCHIVE_MEMBER_PREFIX}{yyyy}/{mm}/"


def find_wp_uploads_refs(text: str) -> list[tuple[str, str, str, str]]:
    """List of (yyyy, mm, file_from_url, full_url)"""
    out = []
    for rx in (WP_UPLOADS_URL, WP_UPLOADS_URL_ANY):
        for m in rx.finditer(text):
            out.append((m.group(1), m.group(2), unquote(m.group(3)), m.group(0)))
    return out


def pick_full_member(
    index_by_key: dict,
    yyyy: str,
    mm: str,
    desired_basename: str,
) -> tuple[str | None, str | None, str]:
    """
    Returns (archive_member_full_or_none, status, notes)
    status: FOUND_FULL | FOUND_SCALED_ONLY | NOT_IN_ARCHIVE
    """
    key_full = (yyyy, mm, desired_basename)
    entries = index_by_key.get(key_full, [])

    full_paths = [e["path"] for e in entries if e["kind"] == "full"]
    scaled_paths = [e["path"] for e in entries if e["kind"] == "scaled"]

    stem, ext = os.path.splitext(desired_basename)
    scaled_name = f"{stem}-scaled{ext}"
    key_scaled = (yyyy, mm, scaled_name)
    scaled_entries = index_by_key.get(key_scaled, [])

    if full_paths:
        # Prefer largest file if multiple (unlikely)
        best = max(full_paths, key=lambda p: next(e["size"] for e in entries if e["path"] == p))
        return best, "FOUND_FULL", ""

    if scaled_paths:
        best = max(scaled_paths, key=lambda p: next(e["size"] for e in entries if e["path"] == p))
        return best, "FOUND_SCALED_ONLY", "only -scaled variant in archive"

    if scaled_entries:
        best = scaled_entries[0]["path"]
        return best, "FOUND_SCALED_ONLY", f"matched {scaled_name}"

    return None, "NOT_IN_ARCHIVE", f"no {desired_basename} under {yyyy}/{mm}"


@dataclass
class Row:
    content_file: str
    reference_kind: str
    current_src: str
    resolved_basename: str
    uploads_yyyy: str
    uploads_mm: str
    archive_tarball: str
    archive_member_full: str
    archive_source_dir: str
    status: str
    destination_dir: str
    destination_file: str
    public_url: str
    notes: str = ""


def iter_markdown_images_and_figures(body: str) -> Iterator[tuple[str, str, str]]:
    """
    Yields (kind, inner_src_or_thumb, outer_url_or_empty)
    kind: md_image | md_linked | figure
    """
    # Linked: [![...](inner)](outer)
    for m in re.finditer(
        r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)", body, re.DOTALL
    ):
        yield "md_linked", m.group(2).strip(), m.group(3).strip()

    # Plain image: ![...](src)  but not inside [![ which we handled — use negative lookbehind tricky; second pass
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", body, re.DOTALL):
        start = m.start()
        if start >= 2 and body[start - 2 : start] == "](":
            continue  # part of md_linked
        yield "md_image", m.group(2).strip(), ""

    for m in FIGURE_SRC.finditer(body):
        yield "figure", m.group(1).strip(), ""


def is_url(s: str) -> bool:
    s = s.strip()
    return s.startswith("http://") or s.startswith("https://") or s.startswith("//")


def resolve_local_src(src: str, md_dir: Path) -> Path | None:
    s = src.strip()
    if is_url(s) or s.startswith("mailto:"):
        return None
    s = unquote(s.split("?")[0].split("#")[0])
    if not s:
        return None
    p = (md_dir / s).resolve()
    try:
        p.relative_to(md_dir.resolve())
    except ValueError:
        return None
    return p


def process_file(
    md_path: Path,
    content_root: Path,
    repo: Path,
    index_by_key: dict,
    basename_index: dict,
    rows: list[Row],
) -> None:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    fm_date = parse_front_matter_date(text)
    dest_relpath = content_dest_relpath(md_path, content_root)
    dest_dir = repo / "static" / dest_relpath if dest_relpath else repo / "static"

    tarball_rel = str(ARCHIVE_TARBALL_REL).replace("\\", "/")

    for kind, inner, outer in iter_markdown_images_and_figures(text):
        current = inner
        if is_url(current):
            rows.append(
                Row(
                    content_file=str(md_path.relative_to(repo)),
                    reference_kind=kind,
                    current_src=current,
                    resolved_basename="",
                    uploads_yyyy="",
                    uploads_mm="",
                    archive_tarball=tarball_rel,
                    archive_member_full="",
                    archive_source_dir="",
                    status="SKIP_ABSOLUTE_SRC",
                    destination_dir=str(dest_dir.relative_to(repo)).replace("\\", "/"),
                    destination_file="",
                    public_url="",
                    notes="remote or absolute URL in markdown",
                )
            )
            continue

        fname = Path(current).name
        if not any(fname.lower().endswith(ext) for ext in IMG_EXT):
            continue

        wp_from_outer: tuple[str, str, str] | None = None
        if outer:
            refs = find_wp_uploads_refs(outer)
            if refs:
                wp_from_outer = (refs[0][0], refs[0][1], refs[0][2])

        if kind == "md_linked" and wp_from_outer:
            # Hi-res already specified by WordPress URL; optional archive check
            yyyy, mm, base_from_url = wp_from_outer[0], wp_from_outer[1], wp_from_outer[2]
            asdir = archive_source_dir(yyyy, mm)
            member, st, note = pick_full_member(index_by_key, yyyy, mm, base_from_url)
            dest_file = dest_dir / base_from_url
            rows.append(
                Row(
                    content_file=str(md_path.relative_to(repo)),
                    reference_kind=kind,
                    current_src=current,
                    resolved_basename=base_from_url,
                    uploads_yyyy=yyyy,
                    uploads_mm=mm,
                    archive_tarball=tarball_rel,
                    archive_member_full=member or "",
                    archive_source_dir=asdir,
                    status=st if member else "NOT_IN_ARCHIVE",
                    destination_dir=str(dest_dir.relative_to(repo)).replace("\\", "/"),
                    destination_file=str(dest_file.relative_to(repo)).replace("\\", "/"),
                    public_url=public_url_from_dest(dest_relpath, base_from_url),
                    notes=("outer wp link; " + note).strip("; "),
                )
            )
            continue

        if not is_resized_basename(fname):
            rows.append(
                Row(
                    content_file=str(md_path.relative_to(repo)),
                    reference_kind=kind,
                    current_src=current,
                    resolved_basename=fname,
                    uploads_yyyy=fm_date[0] if fm_date else "",
                    uploads_mm=fm_date[1] if fm_date else "",
                    archive_tarball=tarball_rel,
                    archive_member_full="",
                    archive_source_dir="",
                    status="SKIP_NO_RESIZE_SUFFIX",
                    destination_dir=str(dest_dir.relative_to(repo)).replace("\\", "/"),
                    destination_file=str((dest_dir / fname).relative_to(repo)).replace("\\", "/"),
                    public_url=public_url_from_dest(dest_relpath, fname),
                    notes="no trailing -WxH; not a WordPress resized name",
                )
            )
            continue

        stripped = strip_all_resize_suffixes(fname)
        yyyy, mm = "", ""
        notes_parts: list[str] = []

        if wp_from_outer:
            yyyy, mm, _ = wp_from_outer
            notes_parts.append("used wp URL from linked outer (inner still resized)")
        elif fm_date:
            yyyy, mm = fm_date
            notes_parts.append("used front matter date for uploads YYYY/MM")
        else:
            rows.append(
                Row(
                    content_file=str(md_path.relative_to(repo)),
                    reference_kind=kind,
                    current_src=current,
                    resolved_basename=stripped,
                    uploads_yyyy="",
                    uploads_mm="",
                    archive_tarball=tarball_rel,
                    archive_member_full="",
                    archive_source_dir="",
                    status="SKIP_NO_DATE_HEURISTIC",
                    destination_dir=str(dest_dir.relative_to(repo)).replace("\\", "/"),
                    destination_file=str((dest_dir / stripped).relative_to(repo)).replace("\\", "/"),
                    public_url=public_url_from_dest(dest_relpath, stripped),
                    notes="no front matter date and no wp URL; cannot resolve uploads folder",
                )
            )
            continue

        asdir = archive_source_dir(yyyy, mm)
        member, st, note = pick_full_member(index_by_key, yyyy, mm, stripped)

        if st == "NOT_IN_ARCHIVE":
            # Post date folder often differs from WordPress upload month (e.g. Dec trip, Jan import).
            hits: list[tuple[str, str, str, str, str]] = []
            for y2, m2, _bn in basename_index.get(stripped, []):
                mem2, st2, n2 = pick_full_member(index_by_key, y2, m2, stripped)
                if st2 in ("FOUND_FULL", "FOUND_SCALED_ONLY") and mem2:
                    hits.append((y2, m2, mem2, st2, n2))
            uniq_folders = {(h[0], h[1]) for h in hits}
            if len(hits) == 1:
                y2, m2, member, st, note = hits[0][0], hits[0][1], hits[0][2], hits[0][3], hits[0][4]
                yyyy, mm = y2, m2
                asdir = archive_source_dir(yyyy, mm)
                notes_parts.append(
                    f"resolved uploads {yyyy}/{mm} via basename index (post date had {fm_date[0]}/{fm_date[1]})"
                    if fm_date
                    else f"resolved uploads {yyyy}/{mm} via basename index"
                )
            elif len(uniq_folders) > 1:
                st = "AMBIGUOUS"
                member = hits[0][2] if hits else ""
                note = (
                    "multiple archive locations for "
                    + stripped
                    + ": "
                    + ", ".join(sorted({f'{a}/{b}' for a, b in uniq_folders}))
                )
                notes_parts.append(note)

        if note and st != "AMBIGUOUS":
            notes_parts.append(note)

        dest_file = dest_dir / stripped
        rows.append(
            Row(
                content_file=str(md_path.relative_to(repo)),
                reference_kind=kind,
                current_src=current,
                resolved_basename=stripped,
                uploads_yyyy=yyyy,
                uploads_mm=mm,
                archive_tarball=tarball_rel,
                archive_member_full=member or "",
                archive_source_dir=asdir,
                status=st,
                destination_dir=str(dest_dir.relative_to(repo)).replace("\\", "/"),
                destination_file=str(dest_file.relative_to(repo)).replace("\\", "/"),
                public_url=public_url_from_dest(dest_relpath, stripped),
                notes="; ".join(notes_parts),
            )
        )


def write_csv(path: Path, rows: list[Row]) -> None:
    if not rows:
        return
    fieldnames = list(asdict(rows[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def write_extract_script(path: Path, repo: Path, members: Iterable[str]) -> None:
    uniq = sorted(set(members))
    lines = [
        "#!/bin/sh",
        "# Auto-generated: extract hi-res originals from WordPress archive into staging.",
        "set -e",
        f'ROOT="{repo}"',
        'cd "$ROOT"',
        'STAGING="${STAGING:-/tmp/hires-restore}"',
        'mkdir -p "$STAGING"',
        f'tar -xzf "{ARCHIVE_TARBALL_REL.as_posix()}" -C "$STAGING" \\',
    ]
    if not uniq:
        lines.append("# (no members to extract)")
    else:
        for i, m in enumerate(uniq):
            suf = " \\" if i < len(uniq) - 1 else ""
            lines.append(f'  "{m}"{suf}')
    lines.append('echo "Extracted to $STAGING"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def summarize(rows: list[Row]) -> str:
    by_status: dict[str, int] = defaultdict(int)
    for r in rows:
        by_status[r.status] += 1
    buf = io.StringIO()
    buf.write("Hi-res image audit summary\n")
    buf.write("==========================\n\n")
    buf.write("Counts by status:\n")
    for k in sorted(by_status, key=lambda x: (-by_status[x], x)):
        buf.write(f"  {k}: {by_status[k]}\n")
    amb = [r for r in rows if r.status == "AMBIGUOUS"]
    if amb:
        buf.write("\nAmbiguous (first 40):\n")
        for r in amb[:40]:
            buf.write(f"  {r.content_file}  {r.current_src}  ->  {r.notes}\n")
        if len(amb) > 40:
            buf.write(f"  ... and {len(amb) - 40} more\n")
    missing = [r for r in rows if r.status == "NOT_IN_ARCHIVE"]
    if missing:
        buf.write("\nNOT_IN_ARCHIVE (first 30):\n")
        for r in missing[:30]:
            buf.write(f"  {r.content_file}  {r.resolved_basename}  {r.uploads_yyyy}/{r.uploads_mm}\n")
        if len(missing) > 30:
            buf.write(f"  ... and {len(missing) - 30} more\n")
    uniq_dest = sorted({r.destination_dir for r in rows if r.destination_dir})
    buf.write(f"\nUnique destination_dir values: {len(uniq_dest)}\n")
    uniq_src = sorted({r.archive_source_dir for r in rows if r.archive_source_dir})
    buf.write(f"Unique archive_source_dir values: {len(uniq_src)}\n")
    return buf.getvalue()


def apply_extract_and_copy(repo: Path, rows: list[Row], tarball: Path) -> None:
    extract_rows = [
        r
        for r in rows
        if r.archive_member_full and r.status in ("FOUND_FULL", "FOUND_SCALED_ONLY")
    ]
    if not extract_rows:
        print("No FOUND_FULL / FOUND_SCALED_ONLY rows to apply.", file=sys.stderr)
        return

    staging = Path(os.environ.get("STAGING", "/tmp/hires-restore"))
    staging.mkdir(parents=True, exist_ok=True)

    members = sorted({r.archive_member_full for r in extract_rows})
    print(f"Extracting {len(members)} members to {staging} (batch) ...", file=sys.stderr)
    with tarfile.open(tarball, "r:gz") as tf:
        infos: list[tarfile.TarInfo] = []
        for m in members:
            try:
                infos.append(tf.getmember(m))
            except KeyError:
                print(f"Member not in tarball: {m}", file=sys.stderr)
        if not infos:
            print("No valid members to extract.", file=sys.stderr)
            return
        # Single pass over tarball (per-member extract() rescans the whole archive).
        try:
            tf.extractall(path=staging, members=infos, filter="data")
        except TypeError:
            tf.extractall(path=staging, members=infos)

    copied = 0
    for r in extract_rows:
        src = staging / r.archive_member_full
        if not src.is_file():
            print(f"Missing after extract: {src}", file=sys.stderr)
            continue
        dst = repo / r.destination_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    print(f"Copied {copied} files into static/", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Extract from tarball and copy FOUND_* files to static/ (see plan Phase 4)",
    )
    args = ap.parse_args()

    repo = repo_root()
    log_path = repo / LS_LOG_REL
    tarball = repo / ARCHIVE_TARBALL_REL
    content_root = repo / "content"

    if not log_path.is_file():
        raise SystemExit(f"Missing {log_path}")
    if not tarball.is_file():
        raise SystemExit(f"Missing {tarball}")

    print("Indexing archive listing ...", file=sys.stderr)
    index_by_key, basename_index = parse_ls_log(log_path)

    rows: list[Row] = []
    for md in sorted(content_root.rglob("*.md")):
        if "themes" in md.parts:
            continue
        rel = md.relative_to(content_root)
        if rel.parts and rel.parts[0] == "themes":
            continue
        process_file(md, content_root, repo, index_by_key, basename_index, rows)

    reports = repo / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    json_path = reports / "hires-image-audit.json"
    csv_path = reports / "hires-image-audit.csv"
    summary_path = reports / "hires-image-audit-summary.txt"
    sh_path = reports / "hires-extract-staging.sh"

    json_path.write_text(
        json.dumps([asdict(r) for r in rows], indent=2), encoding="utf-8"
    )
    write_csv(csv_path, rows)
    summary_path.write_text(summarize(rows), encoding="utf-8")

    extract_members = [
        r.archive_member_full
        for r in rows
        if r.archive_member_full and r.status in ("FOUND_FULL", "FOUND_SCALED_ONLY")
    ]
    write_extract_script(sh_path, repo, extract_members)

    print(f"Wrote {json_path} ({len(rows)} rows)", file=sys.stderr)
    print(f"Wrote {csv_path}", file=sys.stderr)
    print(f"Wrote {summary_path}", file=sys.stderr)
    print(f"Wrote {sh_path} ({len(set(extract_members))} unique tar members)", file=sys.stderr)

    if args.apply:
        apply_extract_and_copy(repo, rows, tarball)


if __name__ == "__main__":
    main()
