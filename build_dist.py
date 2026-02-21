#!/usr/bin/env python3
"""
build_dist.py — Copies only web-server files to /dist
Run from project root: python3 build_dist.py
"""

import os, shutil, glob

ROOT = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"
DIST = os.path.join(ROOT, "dist")

# ── Files/dirs to EXCLUDE from dist ───────────────────────────────────────
EXCLUDE_ROOT_FILES = {
    # Build toolchain
    "package.json", "package-lock.json", "tailwind.config.js",
    "css/input.css",          # Tailwind source — output.css is what browsers need
    # Docs / dev only
    "README.md", "SEO_CONTENT_PROCESS.md", "NEXT MIP v1.pdf",
    # Dev-time components (used by deploy_nav.py, not served)
    "nav-component.html",
    # Python scripts
    "build_dist.py", "deploy_nav.py",
    # Git
    ".gitignore",
}

EXCLUDE_DIRS = {
    "node_modules", ".git", "dist", "templates",
}

# ── HTML pages NOT meant for public serving ────────────────────────────────
EXCLUDE_HTML = {
    "nav-component.html",  # dev component
}

def should_exclude(rel_path):
    parts = rel_path.split(os.sep)
    if parts[0] in EXCLUDE_DIRS:
        return True
    if rel_path in EXCLUDE_ROOT_FILES:
        return True
    if os.path.basename(rel_path) in EXCLUDE_HTML:
        return True
    return False

# ── Web-servable extensions ────────────────────────────────────────────────
SERVE_EXTENSIONS = {".html", ".css", ".js", ".png", ".jpg", ".jpeg",
                    ".gif", ".svg", ".webp", ".ico", ".txt", ".xml",
                    ".json", ".woff", ".woff2", ".ttf", ".eot"}

# Special filenames with no extension to include
SERVE_FILENAMES = {".htaccess", "favicon.ico"}

def is_servable(path):
    _, ext = os.path.splitext(path)
    basename = os.path.basename(path)
    return ext.lower() in SERVE_EXTENSIONS or basename in SERVE_FILENAMES

# ── Clear and rebuild dist ─────────────────────────────────────────────────
print(f"Cleaning {DIST} ...")
# Remove everything except the .gitignore
for item in os.listdir(DIST):
    item_path = os.path.join(DIST, item)
    if item == ".gitignore":
        continue
    if os.path.isdir(item_path):
        shutil.rmtree(item_path)
    else:
        os.remove(item_path)

# ── Walk source and copy ───────────────────────────────────────────────────
copied = []
skipped = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # Prune excluded directories in-place
    dirnames[:] = [d for d in dirnames
                   if d not in EXCLUDE_DIRS and not d.startswith(".")]

    for filename in filenames:
        src_abs = os.path.join(dirpath, filename)
        rel = os.path.relpath(src_abs, ROOT)

        if should_exclude(rel):
            skipped.append(rel)
            continue

        if not is_servable(src_abs):
            skipped.append(rel)
            continue

        dst_abs = os.path.join(DIST, rel)
        os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
        shutil.copy2(src_abs, dst_abs)
        copied.append(rel)

# ── Report ─────────────────────────────────────────────────────────────────
print(f"\n✅ Copied {len(copied)} files to /dist:\n")
for f in sorted(copied):
    size = os.path.getsize(os.path.join(DIST, f))
    print(f"  {f:<65} ({size//1024}KB)" if size >= 1024 else f"  {f:<65} ({size}B)")

print(f"\n⏭  Skipped {len(skipped)} dev/build files.")
print(f"\nDone! /dist is ready for upload.")
