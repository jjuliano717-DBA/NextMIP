#!/usr/bin/env python3
"""
nav_deploy.py — Deploy new nav from nav-component.html to all site pages.

For each target .html page:
  1. Removes old <nav role="navigation">, mobile-menu divs, and old scripts
  2. Ensures head has lucide + google fonts + output.css + styles.css
  3. Injects new nav (style, skip-link, nav element, backdrop, mobile drawer, script)
     immediately after <body ...> tag
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent

# ─── Read nav-component.html and slice out the blocks we need ─────────────────
nav_src = (ROOT / "nav-component.html").read_text(encoding="utf-8")

# 1. <style> block
style_start = nav_src.find('<style>')
style_end = nav_src.find('</style>') + len('</style>')
NAV_STYLE = nav_src[style_start:style_end]

# 2. <nav id="mip-nav"> ... </nav>  (use depth counting)
def extract_balanced(src, open_tag_prefix, close_tag):
    start = src.find(open_tag_prefix)
    if start == -1:
        return ''
    pos = src.find('>', start) + 1  # skip past the opening tag's >
    depth = 1
    while pos < len(src) and depth > 0:
        o = src.find('<' + open_tag_prefix.lstrip('<').split()[0], pos)
        c = src.find(close_tag, pos)
        if c == -1:
            break
        if o != -1 and o < c:
            depth += 1
            pos = o + 1
        else:
            depth -= 1
            if depth == 0:
                return src[start : c + len(close_tag)]
            pos = c + len(close_tag)
    return ''

NAV_ELEMENT = extract_balanced(nav_src, '<nav id="mip-nav"', '</nav>')

# 3. Backdrop
BACKDROP = '    <div id="mip-drawer-backdrop" aria-hidden="true"></div>'

# 4. Mobile drawer
MOBILE_DRAWER = extract_balanced(nav_src, '<div id="mip-mobile-drawer"', '</div>')

# 5. Script — find by known literal
script_start_marker = '<script>\n        (() => {'
script_start = nav_src.find(script_start_marker)
if script_start == -1:
    # Try alternate indent
    script_start = nav_src.find('<script>\n    (() => {')
if script_start != -1:
    script_end = nav_src.find('</script>', script_start) + len('</script>')
    NAV_SCRIPT = nav_src[script_start:script_end]
else:
    NAV_SCRIPT = ''
    print("WARNING: Could not find nav script block!")

# 6. Skip-link
SKIP_LINK = '''    <a href="#main-content"
        class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-cyan-500 focus:text-slate-950 focus:rounded-lg focus:font-bold">Skip
        to main content</a>'''

# Full inject block (inserted right after <body> tag)
NAV_INJECT = (
    '\n\n    ' + NAV_STYLE
    + '\n\n' + SKIP_LINK
    + '\n\n    ' + NAV_ELEMENT
    + '\n\n' + BACKDROP
    + '\n\n    ' + MOBILE_DRAWER
    + '\n\n    ' + NAV_SCRIPT
    + '\n'
)

# ─── Fonts / asset snippets ───────────────────────────────────────────────────
LUCIDE_SCRIPT = '<script src="https://unpkg.com/lucide@latest"></script>'
FONTS_LINK = ('<link href="https://fonts.googleapis.com/css2?family='
              'Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">')


# ─── Per-page config (relative path from ROOT, css_prefix to /css/) ──────────
PAGES = [
    # Root level
    ("index.html",                                      "css/"),
    ("managed-it-vs-managed-intelligence.html",         "css/"),
    ("what-is-a-managed-intelligence-provider.html",    "css/"),
    ("privacy.html",                                    "css/"),
    ("terms.html",                                      "css/"),
    ("sitemap.html",                                    "css/"),
    ("atlanta.html",                                    "css/"),
    ("palm-beach.html",                                 "css/"),
    # Services
    ("services/cybersecurity.html",                     "../css/"),
    ("services/cybersecurity-managed-soc-siem.html",    "../css/"),
    ("services/cloud-services.html",                    "../css/"),
    ("services/managed-it-services.html",               "../css/"),
    ("services/co-managed-it.html",                     "../css/"),
    ("services/predictive-remediation.html",            "../css/"),
    ("services/it-consulting.html",                     "../css/"),
    ("services/index.html",                             "../css/"),
    ("services/tech-debt-audit.html",                   "../css/"),
    # Compliance
    ("compliance/cmmc-2-0.html",                        "../css/"),
    # Industries
    ("industries/healthcare-hitrust.html",              "../css/"),
    ("industries/financial-services.html",              "../css/"),
    ("industries/manufacturing-supply-chain.html",      "../css/"),
    ("industries/employee-benefit-funds.html",          "../css/"),
    # City hubs
    ("atlanta/cybersecurity-compliance.html",           "../css/"),
    ("atlanta/managed-it-services.html",                "../css/"),
    ("palm-beach/it-support-law-firms.html",            "../css/"),
    ("palm-beach/managed-it-services.html",             "../css/"),
    # Resources
    ("resources/cmmc-2-0-survival-guide.html",          "../css/"),
    ("resources/georgia-sled-compliance.html",          "../css/"),
    ("resources/predictive-remediation-manifesto.html", "../css/"),
    ("resources/shadow-ai-revenue-leak.html",           "../css/"),
    # Case studies
    ("case-studies/atlanta-healthcare-ai.html",         "../css/"),
    ("case-studies/palm-beach-defense-cmmc.html",       "../css/"),
    # Templates
    ("templates/article.html",                          "../css/"),
    ("templates/landing.html",                          "../css/"),
    ("templates/page.html",                             "../css/"),
]


# ─── Strip old nav from a page ────────────────────────────────────────────────

def remove_top_level_nav(html: str) -> str:
    """
    Remove the FIRST <nav> with role="navigation" or class="fixed ..."
    that represents the old site nav (not breadcrumbs).
    Uses depth counting to find the matching </nav>.
    """
    # Also strip the preceding <!-- Navigation --> comment if present
    pattern = re.compile(
        r'(?:<!--\s*Navigation\s*-->\s*)?'
        r'<nav\b(?=[^>]*(?:role=["\']navigation["\']|class=["\'][^"\']*fixed))[^>]*>',
        re.IGNORECASE | re.DOTALL
    )
    m = pattern.search(html)
    if not m:
        return html

    start = m.start()
    pos = m.end()   # right after the opening nav tag's >
    depth = 1

    while pos < len(html) and depth > 0:
        o = html.find('<nav', pos)
        c = html.find('</nav>', pos)
        if c == -1:
            break
        if o != -1 and o < c:
            depth += 1
            pos = o + 4
        else:
            depth -= 1
            if depth == 0:
                end = c + len('</nav>')
                # Eat trailing whitespace
                while end < len(html) and html[end] in ' \t\n\r':
                    end += 1
                return html[:start] + html[end:]
            pos = c + 6

    return html


def strip_old_nav(html: str) -> str:
    # 1. Remove old site nav (top-level fixed nav)
    html = remove_top_level_nav(html)

    # 2. Remove old mobile overlay div
    html = re.sub(
        r'(?:<!--\s*Mobile Menu\s*-->\s*)?'
        r'<div\b[^>]*?id=["\']mobile-overlay["\'][^>]*>.*?</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )

    # 3. Remove old lucide + mobile script combo
    html = re.sub(
        r'<script>\s*lucide\.createIcons\(\);'
        r'\s*const mobileBtn.*?</script>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    # Standalone lucide.createIcons() script
    html = re.sub(
        r'<script>\s*lucide\.createIcons\(\);\s*</script>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )

    return html


def ensure_head_assets(html: str, css_prefix: str) -> str:
    """Fix CSS hrefs and ensure all required external assets are linked."""
    output_href = f"{css_prefix}output.css"
    styles_href = f"{css_prefix}styles.css"

    # Fix existing output.css href (any prefix)
    html = re.sub(
        r'(<link\s+rel=["\']stylesheet["\']\s+href=["\'])[^"\']*output\.css(["\']>)',
        rf'\g<1>{output_href}\g<2>',
        html, flags=re.IGNORECASE
    )
    # Fix existing styles.css href (any prefix)
    html = re.sub(
        r'(<link\s+rel=["\']stylesheet["\']\s+href=["\'])[^"\']*styles\.css(["\']>)',
        rf'\g<1>{styles_href}\g<2>',
        html, flags=re.IGNORECASE
    )

    # Add output.css if missing
    if 'output.css' not in html:
        html = html.replace('</head>', f'    <link rel="stylesheet" href="{output_href}">\n</head>', 1)
    # Add styles.css if missing
    if 'styles.css' not in html:
        html = html.replace('</head>', f'    <link rel="stylesheet" href="{styles_href}">\n</head>', 1)
    # Add lucide if missing
    if 'lucide@latest' not in html and 'unpkg.com/lucide' not in html:
        html = html.replace('</head>', f'    {LUCIDE_SCRIPT}\n</head>', 1)
    # Add Google Fonts if missing
    if 'Plus+Jakarta+Sans' not in html and 'Plus Jakarta Sans' not in html:
        html = html.replace('</head>', f'    {FONTS_LINK}\n</head>', 1)

    return html


def inject_nav_after_body(html: str) -> str:
    body_m = re.search(r'<body\b[^>]*>', html, re.IGNORECASE)
    if not body_m:
        print("    WARNING: No <body> tag found — skipping inject!")
        return html
    pos = body_m.end()
    return html[:pos] + NAV_INJECT + html[pos:]


def process_page(rel_path: str, css_prefix: str):
    page_path = ROOT / rel_path
    if not page_path.exists():
        print(f"  SKIP (missing): {rel_path}")
        return

    html = page_path.read_text(encoding="utf-8")
    html = strip_old_nav(html)
    html = ensure_head_assets(html, css_prefix)
    html = inject_nav_after_body(html)
    page_path.write_text(html, encoding="utf-8")
    print(f"  ✓ {rel_path}")


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nParsed nav-component.html ({len(nav_src)} chars):")
    print(f"  style block   : {len(NAV_STYLE)} chars")
    print(f"  nav element   : {len(NAV_ELEMENT)} chars")
    print(f"  mobile drawer : {len(MOBILE_DRAWER)} chars")
    print(f"  script block  : {len(NAV_SCRIPT)} chars")
    print()

    if not NAV_ELEMENT or not NAV_SCRIPT:
        print("ERROR: Missing critical nav blocks. Aborting.")
        exit(1)

    print(f"Deploying to {len(PAGES)} pages...\n")
    for rel_path, css_prefix in PAGES:
        process_page(rel_path, css_prefix)

    print("\nDone. ✓")
