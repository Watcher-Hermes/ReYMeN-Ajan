#!/usr/bin/env python3
"""Check current test import status"""
import os, sys

sys.path.insert(0, '/c/Users/marko/Desktop/Reymen Proje/hermes_projesi')

# Check specific imports
checks = [
    ('utils', 'env_float'),
    ('utils', 'env_int'),
    ('gateway.session', 'SessionEntry'),
    ('gateway.platforms.api_server', 'APIServerAdapter'),
    ('tools.browser_tool', 'cleanup_browser'),
    ('acp_adapter.session', 'SessionManager'),
    ('gateway.platforms.yuanbao', 'YuanbaoClient'),
]

print("=== Kategori Durumu ===")
for mod, sym in checks:
    try:
        exec(f'from {mod} import {sym}')
        print(f"  [OK]  {sym} from {mod}")
    except Exception as e:
        msg = str(e).split('\n')[0][:80]
        print(f"  [FAIL] {sym} from {mod}: {msg}")

# Count remaining import errors in test files
test_dirs = ['tests', 'tests/ReYMeN_reference']
test_files = []
for d in test_dirs:
    if os.path.isdir(d):
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith('.py'):
                    test_files.append(os.path.join(root, f))

print(f"\n=== Test Dosyalari: {len(test_files)} ===")

failed = 0
failed_details = []
for tf in test_files:
    rel = os.path.relpath(tf)
    mod = rel.replace('/', '.').replace('\\', '.').replace('.py', '')
    try:
        __import__(mod)
    except Exception as e:
        failed += 1
        msg = str(e).split('\n')[0][:100]
        failed_details.append((rel, msg))

print(f"Failed imports: {failed} / {len(test_files)}")

# Show top 15 failures
if failed > 0:
    print(f"\n=== Ilk 15 Hata ===")
    for rel, msg in failed_details[:15]:
        print(f"  {rel}: {msg}")

# Group failures by error message
from collections import Counter
error_counts = Counter(msg for _, msg in failed_details)
print(f"\n=== Hata Dagilimi (en sik 10) ===")
for msg, count in error_counts.most_common(10):
    print(f"  [{count}x] {msg[:100]}")
