#!/usr/bin/env python3
"""ReYMeN Daily Memory Backup Push - her gun 00:30, 7 gun."""
import os
import shutil
import subprocess
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen", "cron", "output")
PROJECT_DIR = os.path.join(HOME, "Desktop", "Reymen Proje", "hermes_projesi")
COUNTER = os.path.join(LOG_DIR, "memory_push_counter.txt")
LOG_FILE = os.path.join(LOG_DIR, "daily_memory_push.log")

os.makedirs(LOG_DIR, exist_ok=True)
ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

day_num = 0
try:
    with open(COUNTER) as f:
        day_num = int(f.read().strip())
except (FileNotFoundError, ValueError):
    pass
day_num += 1

with open(COUNTER, "w") as f:
    f.write(str(day_num))

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Day #{day_num} - Starting memory backup push\n")

if not os.path.isdir(PROJECT_DIR):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{ts}] ERROR: Project directory not found\n")
    print(f"HATA: Proje dizini bulunamadı. Day #{day_num}")
    sys.exit(1)

os.chdir(PROJECT_DIR)

# 1. Sync profile state
profile_dir = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen")
snapshot_dir = os.path.join(PROJECT_DIR, ".profile_snapshot")
os.makedirs(snapshot_dir, exist_ok=True)

for fn in ["auth.json", "config.yaml"]:
    src = os.path.join(profile_dir, fn)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(snapshot_dir, fn))

# 2. Git add memory-related files
subprocess.run(
    ["git", "add", ".ReYMeN/", ".profile_snapshot/", "decisions.md", "AGENTS.md"],
    capture_output=True, text=True, timeout=30
)

# 3. Commit
commit = subprocess.run(
    ["git", "commit", "-m", f"memory-backup {ts} -- state + decisions"],
    capture_output=True, text=True, timeout=30
)
commit_ok = commit.returncode == 0

# 4. Push to backup (memory-backup, master)
push = subprocess.run(
    ["git", "push", "backup", "master"],
    capture_output=True, text=True, timeout=60
)
push_ok = push.returncode == 0

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Day #{day_num} - Commit: {commit_ok}, Push: {push_ok}\n")

# Output
print(f"✅ Günlük Memory Backup #{day_num}/7 — {ts}")
print(f"│ Commit      │ {'✅ Yeni commit' if commit_ok else '⚠️  Değişiklik yok'}")
print(f"│ Push        │ {'✅ Başarılı' if push_ok else '❌ Başarısız'}")
print(f"│ Repo        │ Watcher-Hermes/hermes-memory-backup")
print(f"╘═════════════╧════════════════════════════")
print("")
print(f"Kalan gün: {7 - day_num}")
