#!/usr/bin/env python3
"""Code Quality Scan — 5 checks in one run."""
import ast, os, re, sys
from pathlib import Path

PROJECT_DIR = os.path.abspath('.')
DEFAULT_EXCLUDE = {
    'venv', 'bot_venv', 'node_modules', '.git', '__pycache__',
    '.ReYMeN', 'ReYMeN_mirror', 'hermes-memory-backup',
    'desktop', 'dist', 'ReYMeN-full-backup', 'optional-skills',
    'hermes_projesi_eski'
}

def should_skip(root):
    parts = root.replace(os.sep, '/').split('/')
    return any(s in parts for s in DEFAULT_EXCLUDE)

# --- Check 1: Bare except ---
bare_files = []
for root, dirs, files in os.walk(PROJECT_DIR):
    if should_skip(root):
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path, encoding='utf-8') as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    bare_files.append(os.path.relpath(path, PROJECT_DIR).replace(os.sep, '/'))
                    break
        except: pass

print(f'1. Bare except: {len(bare_files)} file(s)')
for p in bare_files[:10]:
    print(f'   {p}')
if len(bare_files) > 10:
    print(f'   ... and {len(bare_files)-10} more')

# --- Check 2: BOM ---
bom_files = []
for root, dirs, files in os.walk(PROJECT_DIR):
    if should_skip(root):
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path, 'rb') as fh:
                data = fh.read()
            if data[:3] == b'\xef\xbb\xbf':
                bom_files.append(os.path.relpath(path, PROJECT_DIR).replace(os.sep, '/'))
        except: pass

print(f'\n2. BOM: {len(bom_files)} file(s)')
for p in bom_files[:10]:
    print(f'   {p}')
if len(bom_files) > 10:
    print(f'   ... and {len(bom_files)-10} more')

# --- Check 3: Syntax ---
ok_count = 0
syn_errors = []
for root, dirs, files in os.walk(PROJECT_DIR):
    if should_skip(root):
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            ast.parse(open(path, encoding='utf-8').read())
            ok_count += 1
        except SyntaxError as e:
            rel = os.path.relpath(path, PROJECT_DIR).replace(os.sep, '/')
            syn_errors.append(f'{rel}: line {e.lineno}: {e.msg}')
        except: pass

print(f'\n3. Syntax: {ok_count} OK, {len(syn_errors)} ERR')
for e in syn_errors[:10]:
    print(f'   ERR: {e}')
if len(syn_errors) > 10:
    print(f'   ... and {len(syn_errors)-10} more')

# --- Check 4: TODO/FIXME ---
patterns = {'TODO': 0, 'FIXME': 0, 'HACK': 0, 'XXX': 0}
details = []
for root, dirs, files in os.walk(PROJECT_DIR):
    if should_skip(root):
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path, errors='replace') as fh:
                for lineno, line in enumerate(fh, 1):
                    for k in patterns:
                        if re.search(r'#\s*' + k + r'\b', line):
                            patterns[k] += 1
                            if patterns[k] <= 10:
                                details.append(f'{os.path.relpath(path, PROJECT_DIR).replace(os.sep, "/")}:{lineno}: {k}')
        except: pass

total_markers = sum(patterns.values())
print(f'\n4. Code markers (total: {total_markers}):')
for k, v in patterns.items():
    print(f'   {k}: {v}')
for d in details[:10]:
    print(f'   {d}')
if len(details) > 10:
    print(f'   ... and {len(details)-10} more')

# --- Check 5: Large files ---
large_files = []
for root, dirs, files in os.walk(PROJECT_DIR):
    if should_skip(root):
        dirs[:] = []
        continue
    dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDE]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path, encoding='utf-8', errors='ignore') as fh:
                lines = len(fh.readlines())
            if lines > 500:
                large_files.append((lines, os.path.relpath(path, PROJECT_DIR).replace(os.sep, '/')))
        except: pass
large_files.sort(reverse=True)

print(f'\n5. Large files (>500 lines): {len(large_files)}')
for lines, path in large_files[:10]:
    print(f'   {lines:5d} lines  {path}')
if len(large_files) > 10:
    print(f'   ... and {len(large_files)-10} more')

# Summary
print(f'\n=== SUMMARY: BareExcept:{len(bare_files)} BOM:{len(bom_files)} SyntaxOK:{ok_count} SyntaxERR:{len(syn_errors)} TODO:{total_markers} LargeFiles:{len(large_files)} ===')
