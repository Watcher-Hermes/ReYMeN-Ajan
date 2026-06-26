#!/usr/bin/env python3
"""Skills .md dosyalarındaki eski Hermes import'larını güncelle."""

import re
import os
import glob

SKILLS_DIR = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills"

# Eski -> Yeni mapping
MAPPINGS = [
    (r'\bfrom tools\.', 'from reymen.hermes.tools.'),
    (r'\bimport tools\.', 'import reymen.hermes.tools.'),
    (r'\bfrom agent\.', 'from reymen.hermes.agent.'),
    (r'\bimport agent\.', 'import reymen.hermes.agent.'),
    (r'\bfrom gateway\.', 'from reymen.hermes.gateway.'),
    (r'\bimport gateway\.', 'import reymen.hermes.gateway.'),
    (r'\bfrom plugins\.', 'from reymen.hermes.plugins.'),
    (r'\bimport plugins\.', 'import reymen.hermes.plugins.'),
    (r'\bfrom cron\.', 'from reymen.hermes.cron.'),
    (r'\bimport cron\.', 'import reymen.hermes.cron.'),
    (r'\bfrom acp\.', 'from reymen.hermes.acp.'),
    (r'\bimport acp\.', 'import reymen.hermes.acp.'),
    (r'\bfrom apps\.', 'from reymen.hermes.apps.'),
    (r'\bimport apps\.', 'import reymen.hermes.apps.'),
    (r'\bfrom tui_gateway\.', 'from reymen.hermes.tui_gateway.'),
    (r'\bimport tui_gateway\.', 'import reymen.hermes.tui_gateway.'),
    (r'\bfrom scripts\.', 'from reymen.hermes.scripts.'),
    (r'\bimport scripts\.', 'import reymen.hermes.scripts.'),
    (r'\bfrom telegram_bot\.', 'from reymen.hermes.telegram_bot.'),
    (r'\bimport telegram_bot\.', 'import reymen.hermes.telegram_bot.'),
]

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_content = content
    for pattern, replacement in MAPPINGS:
        content = re.sub(pattern, replacement, content)
    
    if content != old_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Tüm .md dosyalarını tara
changed = 0
total = 0
for root, dirs, files in os.walk(SKILLS_DIR):
    for f in files:
        if f.endswith('.md'):
            total += 1
            fp = os.path.join(root, f)
            if update_file(fp):
                changed += 1
                print(f"  ✅ {os.path.relpath(fp, SKILLS_DIR)}")

print(f"\nToplam: {total} .md dosya taranndı, {changed}'inde değişiklik yapıldı.")
