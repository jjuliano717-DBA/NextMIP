#!/usr/bin/env python3
import os
import re

ROOT_DIR = "/Volumes/HomeX/jasonmini/Documents/Projects/NextMIP"
TARGET_STRING = '<script src="https://unpkg.com/lucide@latest" onload="lucide.createIcons()"></script>'
REPLACEMENT_STRING = '<script defer src="https://unpkg.com/lucide@latest" onload="lucide.createIcons()"></script>'

def optimize_js():
    modified_count = 0
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip dist and node_modules
        if "dist" in root or "node_modules" in root or ".git" in root:
            continue
            
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if TARGET_STRING in content:
                    new_content = content.replace(TARGET_STRING, REPLACEMENT_STRING)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Modified {filepath}")
                    modified_count += 1
                elif REPLACEMENT_STRING in content:
                    print(f"Skipping {filepath} (Already optimized)")
                else:
                    print(f"Warning: Could not find target script in {filepath}")
    
    print(f"\nDone! Modified {modified_count} files.")

if __name__ == "__main__":
    optimize_js()
