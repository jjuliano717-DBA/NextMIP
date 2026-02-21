#!/usr/bin/env python3
import os
import re

ROOT_DIR = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"
GA_TAG_ID = "G-WDN2287H4D"
GA_SNIPPET = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_TAG_ID}');
</script>"""

def inject_ga_tag():
    modified_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip dist and node_modules
        if "dist" in root or "node_modules" in root or ".git" in root:
            continue
            
        for file in files:
            if file.endswith(".html") and file != "nav-component.html":
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # check for existing tag
                if GA_TAG_ID in content:
                    print(f"Skipping {filepath} (Tag already present)")
                    skipped_count += 1
                    continue
                
                # inject after <head>
                # using case-insensitive regex for <head>
                new_content = re.sub(r'(<head\b[^>]*>)', r'\1\n' + GA_SNIPPET, content, count=1, flags=re.IGNORECASE)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Modified {filepath}")
                    modified_count += 1
                else:
                    print(f"Warning: Could not find <head> in {filepath}")
    
    print(f"\nDone! Modified {modified_count} files, skipped {skipped_count} files.")

if __name__ == "__main__":
    inject_ga_tag()
