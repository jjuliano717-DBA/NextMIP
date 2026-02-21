#!/usr/bin/env python3
"""
fix_icons_footer.py
────────────────────────────────────────────────────────────────────────────
Fixes all subpages for:
  1. Lucide icon loading — adds onload="lucide.createIcons()" and a
     DOMContentLoaded fallback so icons always render.
  2. Replaces data-lucide social icons in footers with inline SVGs so they
     work even before JS loads (or if CDN is slow).
  3. Adds "About Us" to the Company section of every footer.
"""

import os, re, glob

ROOT = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"

# ── Inline SVGs for social icons (always visible, no JS dependency) ────────
SOCIAL_SVG = {
    "facebook": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-label="Facebook"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
    "linkedin": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-label="LinkedIn"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>',
    "twitter":  '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-label="X / Twitter"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    "youtube":  '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-label="YouTube"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-1.96C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 1.96A29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58A2.78 2.78 0 0 0 3.4 19.54C5.12 20 12 20 12 20s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-1.96A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z"/><polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="#020617"/></svg>',
}

# Social icon button wrapper (matches index.html styling)
def social_btn(platform, href="#"):
    svg = SOCIAL_SVG[platform]
    return (f'<a href="{href}" aria-label="{platform.capitalize()}" '
            f'class="w-10 h-10 rounded-lg bg-slate-900 border border-white/10 '
            f'flex items-center justify-center text-white hover:text-cyan-400 '
            f'hover:border-cyan-500/30 transition-all">{svg}</a>')

SOCIAL_BLOCK = (
    '<div class="flex gap-4">\n'
    f'                    {social_btn("facebook")}\n'
    f'                    {social_btn("linkedin")}\n'
    f'                    {social_btn("twitter")}\n'
    f'                    {social_btn("youtube")}\n'
    '                </div>'
)

# ── Patterns ───────────────────────────────────────────────────────────────

# Old social block using data-lucide (multi-line)
OLD_SOCIAL_PATTERN = re.compile(
    r'<div class="flex gap-4">.*?</div>',
    re.DOTALL
)

# Lucide script WITHOUT onload
LUCIDE_NO_ONLOAD = re.compile(
    r'<script src="https://unpkg\.com/lucide@latest"></script>'
)
LUCIDE_WITH_ONLOAD = '<script src="https://unpkg.com/lucide@latest" onload="lucide.createIcons()"></script>'

# DOMContentLoaded fallback to add if not already present (before </body>)
LUCIDE_FALLBACK = '''
    <!-- Lucide icon fallback: ensures icons render even if onload fires before DOM is ready -->
    <script>
    (function() {
        function tryIcons() { if (typeof lucide !== 'undefined') lucide.createIcons(); }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', tryIcons);
        } else {
            tryIcons();
        }
        // Also re-run after a short delay to catch any dynamic content
        setTimeout(tryIcons, 800);
    })();
    </script>'''

# Company footer section — old (without About Us)
COMPANY_SECTION_OLD = re.compile(
    r'(<h4[^>]*>Company</h4>\s*<ul[^>]*>)(.*?)(</ul>)',
    re.DOTALL | re.IGNORECASE
)
ABOUT_LINK = '<li><a href="/about.html" class="hover:text-cyan-400 transition-colors">About Us</a></li>'

# ── Process each HTML file ─────────────────────────────────────────────────
html_files = glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True)
html_files = [f for f in html_files
              if "node_modules" not in f
              and "/dist/" not in f
              and "/.git/" not in f]

results = []

for fpath in sorted(html_files):
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content
    fixes = []

    # ── 1. Fix Lucide script tag ──────────────────────────────────────────
    if LUCIDE_NO_ONLOAD.search(content):
        content = LUCIDE_NO_ONLOAD.sub(LUCIDE_WITH_ONLOAD, content)
        fixes.append("Lucide onload")

    # ── 2. Add DOMContentLoaded fallback if not present ───────────────────
    if 'lucide' in content and 'DOMContentLoaded' not in content and '</body>' in content:
        content = content.replace('</body>', LUCIDE_FALLBACK + '\n</body>', 1)
        fixes.append("Lucide fallback")

    # ── 3. Replace data-lucide social icons with inline SVGs ──────────────
    # Find the social media flex div in footers and replace i[data-lucide] with inline SVG
    for platform, svg in SOCIAL_SVG.items():
        # Replace <i data-lucide="platform" ...></i> inside the footer
        old_icon = re.compile(
            rf'<i\s+data-lucide="{platform}"[^>]*>\s*</i>',
            re.IGNORECASE
        )
        if old_icon.search(content):
            content = old_icon.sub(svg, content)
            fixes.append(f"SVG:{platform}")

    # ── 4. Add About Us to Company footer section ─────────────────────────
    def add_about(m):
        ul_open = m.group(1)
        ul_body = m.group(2)
        ul_close = m.group(3)
        # Don't add if already there
        if '/about.html' in ul_body or 'About Us' in ul_body:
            return m.group(0)
        return ul_open + '\n                    ' + ABOUT_LINK + ul_body + ul_close

    new_content = COMPANY_SECTION_OLD.sub(add_about, content)
    if new_content != content:
        fixes.append("About Us in footer")
        content = new_content

    # ── Save if changed ───────────────────────────────────────────────────
    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        rel = os.path.relpath(fpath, ROOT)
        results.append((rel, fixes))

# ── Report ─────────────────────────────────────────────────────────────────
print(f"Fixed {len(results)} files:\n")
for rel, fixes_list in results:
    print(f"  {rel:<65} {', '.join(fixes_list)}")

# Final audit
print("\n=== AUDIT: remaining data-lucide social icons in footers ===")
remaining = 0
for fpath in html_files:
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        c = f.read()
    # Check footer area for data-lucide social icons
    footer_m = re.search(r'<footer.*</footer>', c, re.DOTALL)
    if footer_m:
        footer = footer_m.group(0)
        icons = re.findall(r'data-lucide="(facebook|linkedin|twitter|youtube)"', footer)
        if icons:
            print(f"  REMAINING: {os.path.relpath(fpath, ROOT)} — {icons}")
            remaining += 1
if not remaining:
    print("  ✅ No data-lucide social icons remaining in any footer.")

print("\n=== AUDIT: Lucide script without onload ===")
missing_onload = 0
for fpath in html_files:
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        c = f.read()
    if LUCIDE_NO_ONLOAD.search(c):
        print(f"  STILL MISSING onload: {os.path.relpath(fpath, ROOT)}")
        missing_onload += 1
if not missing_onload:
    print("  ✅ All Lucide scripts have onload=createIcons().")

print("\nDone!")
