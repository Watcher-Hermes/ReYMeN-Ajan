#!/usr/bin/env python3
"""ReYMeN 15-dakikada bir test kosucusu."""
import os
import subprocess
import sys
from datetime import datetime

HOME = os.path.expanduser("~")
PROJECT_DIR = os.path.join(HOME, "Desktop", "Reymen Proje", "hermes_projesi")
LOG_DIR = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen", "cron", "output")
COUNTER = os.path.join(LOG_DIR, "test_counter.txt")
LOG_FILE = os.path.join(LOG_DIR, "test_runner.log")

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

if not os.path.isdir(PROJECT_DIR):
    print(f"[{ts}] HATA: Proje dizini yok")
    sys.exit(1)

os.chdir(PROJECT_DIR)

# Run key tests (quick subset, ~10-15sn)
result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/ReYMeN_reference/acp/test_auth.py",
     "tests/ReYMeN_reference/acp/test_server.py",
     "-q", "--tb=line", "-p", "no:capture"],
    capture_output=True, text=True, timeout=60
)

passed = "passed" in result.stdout
with open(LOG_FILE, "a") as log:
    log.write(f"[{ts}] Run #{run_num}: {'PASS' if passed else 'FAIL'}\n")
    if result.stdout:
        log.write(result.stdout[-200:] + "\n")

print(f"🧪 Test #{run_num} — {ts}")
print(result.stdout.strip())
