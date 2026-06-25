#!/usr/bin/env python3
"""ReYMeN Hourly Check Script - her saat, 24x7 = 168 kez."""
import os
import subprocess
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen", "cron", "output")
PROJECT_DIR = os.path.join(HOME, "Desktop", "Reymen Proje", "hermes_projesi")
COUNTER = os.path.join(LOG_DIR, "hourly_counter.txt")
LOG_FILE = os.path.join(LOG_DIR, "hourly_check.log")

os.makedirs(LOG_DIR, exist_ok=True)

ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

run_num = 0
try:
    with open(COUNTER) as f:
        run_num = int(f.read().strip())
except (FileNotFoundError, ValueError):
    pass
run_num += 1

with open(COUNTER, "w") as f:
    f.write(str(run_num))

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Run #{run_num} - Starting hourly check\n")

if not os.path.isdir(PROJECT_DIR):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{ts}] ERROR: Project directory not found\n")
    print(f"HATA: Proje dizini bulunamadı. Run #{run_num}")
    sys.exit(1)

os.chdir(PROJECT_DIR)

# 1. Git status
try:
    changes = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
    change_count = len([l for l in changes.stdout.split("\n") if l.strip()])
    commits = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, timeout=10)
    commit_count = commits.stdout.strip()
except Exception as e:
    change_count, commit_count = "?", "?"
    with open(LOG_FILE, "a") as log:
        log.write(f"[{ts}] Git error: {e}\n")

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Git: {change_count} modified files, {commit_count} total commits\n")

# 2. Check remotes
remote_status = {}
for remote in ["origin", "full-backup", "backup"]:
    try:
        r = subprocess.run(["git", "ls-remote", remote, "HEAD"], capture_output=True, text=True, timeout=10)
        ok = r.returncode == 0 and r.stdout.strip()
        remote_status[remote] = "OK" if ok else "FAIL"
    except Exception as e:
        remote_status[remote] = "FAIL"

with open(LOG_FILE, "a") as log:
    for name, status in remote_status.items():
        log.write(f"[{ts}] Remote {name}: {status}\n")

with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Run #{run_num} - Completed\n")

# Output
remote_ok = sum(1 for v in remote_status.values() if v == "OK")
print(f"✅ Saatlik Kontrol #{run_num} — {ts}")
print(f"│ Değişiklik  │ {change_count} dosya")
print(f"│ Commit      │ {commit_count} adet")
print(f"│ Remote      │ {remote_ok}/3 erişilebilir")
print(f"╘═════════════╧═════════════════")
print("")
print(f"7 gün/168 koşu hedefleniyor. Kalan: {168 - run_num}")
