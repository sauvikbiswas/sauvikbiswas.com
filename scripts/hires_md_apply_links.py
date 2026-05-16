#!/usr/bin/env python3
"""
Apply hi-res links to Hugo Markdown using reports/hires-image-audit.json.

Run `python3 scripts/hires_image_audit.py` after adding imports or static files,
then dry-run this tool, then `--write`.

  python3 scripts/hires_md_apply_links.py              # dry-run (default)
  python3 scripts/hires_md_apply_links.py --write      # patch content/**/*.md
  python3 scripts/hires_md_apply_links.py --only content/posts/foo/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from hires_common import FIGURE_SRC  # noqa: E402

ELIGIBLE = frozenset({"FOUND_FULL", "FOUND_SCALED_ONLY"})

MD_LINKED = re.compile(
    r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)",
    re.DOTALL,
)
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)", re.DOTALL)
FIGURE_LINK_ATTR = re.compile(r"(?i)\blink\s*=")
FIGURE_LINK_VALUE = re.compile(
    r'(?i)\blink\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)'
)


def repo_root() -> Path:
    p = Path(__file__).resolve().parent.parent
    if (p / "hugo.toml").is_file():
        return p
    raise SystemExit("Run from sauvikbiswas.com repo (hugo.toml not found)")


def norm_url_path(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("/"):
        return unquote(url.rstrip("/"))
    p = urlparse(url)
    return unquote((p.path or "").rstrip("/"))


def urls_equivalent(a: str, b: str) -> bool:
    return norm_url_path(a) == norm_url_path(b)


def is_wpish_upload_url(url: str) -> bool:
    u = url.strip().lower()
    return "wp-content/uploads" in u and (
        "sauvikbiswas.com" in u or u.startswith("http://") or u.startswith("https://")
    )


def build_maps(
    rows: list[dict],
) -> tuple[dict[tuple[str, str, str], str], set[tuple[str, str]]]:
    """(content_file, reference_kind, current_src) -> public_url; linked_inner pairs."""
    patch: dict[tuple[str, str, str], str] = {}
    linked_inner: set[tuple[str, str]] = set()
    for row in rows:
        if row.get("status") not in ELIGIBLE:
            continue
        pub = (row.get("public_url") or "").strip()
        if not pub:
            continue
        cf = (row.get("content_file") or "").strip().replace("\\", "/")
        rk = (row.get("reference_kind") or "").strip()
        cs = (row.get("current_src") or "").strip()
        if not cf or not rk or not cs:
            continue
        key = (cf, rk, cs)
        patch.setdefault(key, pub)
        if rk == "md_linked":
            linked_inner.add((cf, cs))
    return patch, linked_inner


def collect_edits(
    text: str,
    content_file: str,
    patch: dict[tuple[str, str, str], str],
    linked_inner: set[tuple[str, str]],
) -> list[tuple[int, int, str]]:
    edits: list[tuple[int, int, str]] = []

    # md_linked: replace outer href when map has key and outer is wp-ish
    for m in MD_LINKED.finditer(text):
        inner, outer = m.group(2).strip(), m.group(3).strip()
        key = (content_file, "md_linked", inner)
        if key not in patch:
            continue
        pub = patch[key]
        if urls_equivalent(outer, pub):
            continue
        if not is_wpish_upload_url(outer):
            continue
        s, e = m.span(3)
        edits.append((s, e, pub))

    # figure: insert link="..." before >}}
    for m in FIGURE_SRC.finditer(text):
        src = m.group(1).strip()
        key = (content_file, "figure", src)
        if key not in patch:
            continue
        pub = patch[key]
        full = m.group(0)
        if FIGURE_LINK_ATTR.search(full):
            mv = FIGURE_LINK_VALUE.search(full)
            if mv:
                raw = mv.group(1).strip("\"'")
                if urls_equivalent(raw, pub) or raw == pub:
                    continue
            continue
        idx = full.rfind(">}}")
        if idx < 0 or full[idx : idx + 3] != ">}}":
            continue
        new_full = full[:idx] + f' link="{pub}"' + full[idx:]
        edits.append((m.start(), m.end(), new_full))

    # md_image: wrap in link (skip inner of md_linked; skip already wrapped)
    for m in MD_IMAGE.finditer(text):
        start = m.start()
        if start >= 2 and text[start - 2 : start] == "](":
            continue
        # Inner image of [![](thumb)](url): '!' is immediately preceded by '['
        if start >= 1 and text[start - 1] == "[":
            continue
        inner_src = m.group(2).strip()
        key = (content_file, "md_image", inner_src)
        if key not in patch:
            continue
        if (content_file, inner_src) in linked_inner:
            continue
        pub = patch[key]
        alt = m.group(1)
        wrapped = f"[![{alt}]({inner_src})]({pub})"
        if text[start : start + len(wrapped)] == wrapped:
            continue
        edits.append((m.start(), m.end(), wrapped))

    return edits


def apply_edits(text: str, edits: list[tuple[int, int, str]]) -> str:
    for s, e, new in sorted(edits, key=lambda x: -x[0]):
        text = text[:s] + new + text[e:]
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--audit",
        type=Path,
        default=Path("reports/hires-image-audit.json"),
        help="Path to hires-image-audit.json (repo-relative or absolute)",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Write patched files (default is dry-run)",
    )
    ap.add_argument(
        "--only",
        type=str,
        default="",
        help="Only process content files whose path starts with this prefix (e.g. content/posts/foo/)",
    )
    args = ap.parse_args()

    repo = repo_root()
    audit_path = args.audit if args.audit.is_absolute() else repo / args.audit
    if not audit_path.is_file():
        raise SystemExit(f"Missing audit file: {audit_path}")

    rows = json.loads(audit_path.read_text(encoding="utf-8"))
    patch, linked_inner = build_maps(rows)

    content_files = sorted({k[0] for k in patch if k[0].startswith("content/")})
    if args.only:
        pref = args.only.strip().replace("\\", "/")
        content_files = [c for c in content_files if c.startswith(pref)]

    by_file: dict[str, list[tuple[int, int, str]]] = {}
    for cf in content_files:
        p = repo / cf
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8")
        ed = collect_edits(body, cf, patch, linked_inner)
        if ed:
            by_file[cf] = ed

    total_edits = sum(len(v) for v in by_file.values())
    print(f"Files with edits: {len(by_file)}  Total replacement spans: {total_edits}", file=sys.stderr)
    for cf, ed in sorted(by_file.items())[:15]:
        print(f"  {cf}: {len(ed)}", file=sys.stderr)
    if len(by_file) > 15:
        print(f"  ... and {len(by_file) - 15} more", file=sys.stderr)

    if not args.write:
        print("Dry-run only. Pass --write to apply.", file=sys.stderr)
        return

    for cf, ed in by_file.items():
        p = repo / cf
        body = p.read_text(encoding="utf-8")
        new_body = apply_edits(body, ed)
        p.write_text(new_body, encoding="utf-8", newline="")

    print(f"Wrote {len(by_file)} files.", file=sys.stderr)


if __name__ == "__main__":
    main()
