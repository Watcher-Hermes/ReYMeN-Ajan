#!/usr/bin/env python3
"""ReYMeN Daily Full Backup Push - her gun 03:00, 7 gun."""
import os
import shutil
import subprocess
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen", "cron", "output")
PROJECT_DIR = os.path.join(HOME, "Desktop", "Reymen Proje", "hermes_projesi")
COUNTER = os.path.join(LOG_DIR, "full_push_counter.txt")
LOG_FILE = os.path.join(LOG_DIR, "daily_full_push.log")

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
    log.write(f"[{ts}] Day #{day_num} - Starting full backup push\n")

if not os.path.isdir(PROJECT_DIR):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{ts}] ERROR: Project directory not found\n")
    print(f"HATA: Proje dizini bulunamadı. Day #{day_num}")
    sys.exit(1)

os.chdir(PROJECT_DIR)

# 1. Add all changes
subprocess.run(["git", "add", "-A"], capture_output=True, text=True, timeout=30)

# 2. Commit
commit = subprocess.run(
    ["git", "commit", "-m", f"auto-backup {ts} -- full project"],
    capture_output=True, text=True, timeout=30
)
commit_ok = commit.returncode == 0

# 3. Push to full-backup
push = subprocess.run(
    ["git", "push", "full-backup", "main"],
    capture_output=True, text=True, timeout=60
)
push_ok = push.returncode == 0

# 4. Backup profile state
profile_backup = os.path.join(PROJECT_DIR, ".profile_backup")
profile_dir = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen")
if os.path.isdir(profile_dir):
    if os.path.isdir(profile_backup):
        shutil.rmtree(profile_backup)
    shutil.copytree(profile_dir, profile_backup, ignore=shutil.ignore_patterns(".env"))
    # Remove sensitive files
    env_file = os.path.join(profile_backup, ".env")
    if os.path.isfile(env_file):
        os.remove(env_file)

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Day #{day_num} - Commit: {commit_ok}, Push: {push_ok}\n")

# Output
print(f"✅ Günlük Full Backup #{day_num}/7 — {ts}")
print(f"│ Commit      │ {'✅ Yeni commit' if commit_ok else '⚠️  Değişiklik yok'}")
print(f"│ Push        │ {'✅ Başarılı' if push_ok else '❌ Başarısız'}")
print(f"│ Repo        │ Watcher-Hermes/hermes-full-backup")
print(f"╘═════════════╧════════════════════════════")
print("")
print(f"Kalan gün: {7 - day_num}")
