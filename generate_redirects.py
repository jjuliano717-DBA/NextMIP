#!/usr/bin/env python3
"""Creates index.html redirect pages for directories missing them."""

import os

ROOT = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"

# (directory, redirect target, page title)
REDIRECTS = [
    ("palm-beach",   "/palm-beach.html",                          "Palm Beach Managed IT"),
    ("atlanta",      "/atlanta.html",                             "Atlanta Managed IT"),
    ("industries",   "/services/index.html",                      "Industries — Next MIP"),
    ("compliance",   "/compliance/cmmc-2-0.html",                 "Compliance — Next MIP"),
    ("case-studies", "/case-studies/atlanta-healthcare-ai.html",  "Case Studies — Next MIP"),
    ("resources",    "/resources/predictive-remediation-manifesto.html", "Resources — Next MIP"),
]

TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Redirecting | {title}</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="https://nextmip.com{target}">
<script>window.location.replace("{target}");</script>
</head>
<body>
<p>Redirecting to <a href="{target}">{title}</a>&hellip;</p>
</body>
</html>
"""

for dirpath, target, title in REDIRECTS:
    out = os.path.join(ROOT, dirpath, "index.html")
    html = TEMPLATE.format(target=target, title=title)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Created: {dirpath}/index.html  →  {target}")

print("\nDone.")
