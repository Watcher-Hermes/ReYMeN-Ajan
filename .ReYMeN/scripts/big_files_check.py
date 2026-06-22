import os

skip_dirs = ['venv', 'bot_venv', 'node_modules', '.git', '__pycache__',
             '.ReYMeN', 'ReYMeN_mirror', 'hermes-memory-backup',
             'desktop', 'dist', 'ReYMeN-full-backup', 'optional-skills']
big_files = []
total_py = 0
for root, dirs, files in os.walk('.'):
    parts = root.replace(os.sep, '/').split('/')
    if any(s in parts for s in skip_dirs):
        continue
    for f in files:
        if f.endswith('.py'):
            total_py += 1
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    lines = len(fh.readlines())
                if lines > 500:
                    big_files.append((lines, path.replace(os.sep, '/').replace('./', '')))
            except Exception:
                pass

big_files.sort(reverse=True)
print(f"Total .py files scanned: {total_py}")
print(f"Files >500 lines: {len(big_files)}")
print()
for lines, path in big_files[:20]:
    print(f'{lines:5d} lines  {path}')
if len(big_files) > 20:
    print(f'... and {len(big_files) - 20} more')
