#!/usr/bin/env python3
"""
audit_links.py — Full internal-link audit for NextMIP
Finds every href that would produce a 404 on the live server.
"""

import os, re, glob
from urllib.parse import urlparse, unquote

ROOT = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"

# Collect all HTML source files (not dist/)
html_files = sorted(glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True))
html_files = [f for f in html_files
              if "/dist/" not in f
              and "/node_modules/" not in f
              and "/.git/" not in f]

# Build set of all files that WILL be in /dist (relative paths from ROOT)
# These are the files that will actually exist on the server
SKIP_EXT = {".py", ".md", ".pdf", ".json", ".lock", ".js", ".config"}
served_files = set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames
                  if d not in {"node_modules", ".git", "dist", "templates"}
                  and not d.startswith(".")]
    for fname in filenames:
        abs_path = os.path.join(dirpath, fname)
        rel = "/" + os.path.relpath(abs_path, ROOT)
        ext = os.path.splitext(fname)[1].lower()
        if ext not in SKIP_EXT and not fname.startswith("."):
            served_files.add(rel)

# Also add directory index.html as the dir path itself
for f in list(served_files):
    if f.endswith("/index.html"):
        served_files.add(f[:-len("index.html")])
        served_files.add(f[:-len("/index.html")])

# ── Extract and resolve all internal hrefs ─────────────────────────────────
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:")
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']')

broken = []      # (source_file, href, resolved)
ok_count = 0

for fpath in html_files:
    page_rel   = "/" + os.path.relpath(fpath, ROOT)  # e.g. /services/cybersecurity.html
    page_dir   = os.path.dirname(page_rel)            # e.g. /services

    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    hrefs = HREF_RE.findall(content)
    hrefs = set(hrefs)  # deduplicate per page

    for href in hrefs:
        href = href.strip()

        # Skip external, anchor-only, special schemes
        if any(href.startswith(p) for p in SKIP_PREFIXES):
            continue

        # Strip fragment
        href_path = href.split("#")[0]
        if not href_path:
            continue

        # Resolve to absolute server path
        if href_path.startswith("/"):
            resolved = href_path
        else:
            # relative to page dir
            resolved = os.path.normpath(os.path.join(page_dir, href_path))
            if not resolved.startswith("/"):
                resolved = "/" + resolved

        # Normalise double slashes
        resolved = re.sub(r"//+", "/", resolved)

        # Check if the resolved path exists in served files
        # Exact match OR with /index.html appended
        exists = (resolved in served_files
                  or resolved + ".html" in served_files
                  or (resolved.rstrip("/") + "/index.html") in served_files
                  or resolved + "/index.html" in served_files)

        if exists:
            ok_count += 1
        else:
            broken.append((os.path.relpath(fpath, ROOT), href, resolved))

# ── Report ─────────────────────────────────────────────────────────────────
print(f"✅ OK links: {ok_count}")
print(f"❌ BROKEN links: {len(broken)}\n")

if broken:
    # Group by source file
    from collections import defaultdict
    by_file = defaultdict(list)
    for src, href, resolved in broken:
        by_file[src].append((href, resolved))

    for src, items in sorted(by_file.items()):
        print(f"\n📄 {src}")
        for href, resolved in items:
            print(f"     href: {href:<55} → {resolved}")

print("\n=== All served files ===")
for f in sorted(served_files):
    if f.endswith(".html"):
        print(f"  {f}")
