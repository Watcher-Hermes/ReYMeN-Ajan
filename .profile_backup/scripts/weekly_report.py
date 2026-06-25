#!/usr/bin/env python3
"""ReYMeN 7-Day Report - 7 gun sonra calisir."""
import os
import subprocess
from datetime import datetime

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "AppData", "Local", "hermes", "profiles", "reymen", "cron", "output")
PROJECT_DIR = os.path.join(HOME, "Desktop", "Reymen Proje", "hermes_projesi")

ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_counter(name):
    path = os.path.join(LOG_DIR, name)
    try:
        with open(path) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

hourly_count = read_counter("hourly_counter.txt")
full_count = read_counter("full_push_counter.txt")
mem_count = read_counter("memory_push_counter.txt")

print("═══════════════════════════════════════════════")
print(f"   ReYMeN 7 Günlük Backup Raporu")
print(f"   {ts}")
print("═══════════════════════════════════════════════")
print("")

# Hourly check
print("📊 Saatlik Kontrol")
print(f"   Beklenen: 168  Gerçekleşen: {hourly_count}")
if hourly_count >= 168:
    print("   Durum: ✅ TAM")
else:
    print(f"   Durum: ⚠️  Eksik: {168 - hourly_count}")
print("")

# Full backup
print("📦 Full Backup (03:00)")
print(f"   Beklenen: 7  Gerçekleşen: {full_count}")
if full_count >= 7:
    print("   Durum: ✅ TAM")
else:
    print(f"   Durum: ⚠️  Eksik: {7 - full_count}")
print("")

# Memory backup
print("🧠 Memory Backup (00:30)")
print(f"   Beklenen: 7  Gerçekleşen: {mem_count}")
if mem_count >= 7:
    print("   Durum: ✅ TAM")
else:
    print(f"   Durum: ⚠️  Eksik: {7 - mem_count}")
print("")

# Git status
if os.path.isdir(PROJECT_DIR):
    os.chdir(PROJECT_DIR)
    print("🔗 Son Git Durumu")
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        last_msg = subprocess.run(["git", "log", "-1", "--format=%s"], capture_output=True, text=True, timeout=10)
        print(f"   Origin:      {head.stdout.strip()} -- {last_msg.stdout.strip()}")
    except Exception:
        print("   Origin:      N/A")
    try:
        fb = subprocess.run(["git", "ls-remote", "full-backup", "HEAD"], capture_output=True, text=True, timeout=10)
        fb_hash = fb.stdout.split()[0][:7] if fb.stdout.strip() else "N/A"
        print(f"   Full-Backup: {fb_hash}")
    except Exception:
        print("   Full-Backup: N/A")
    try:
        mb = subprocess.run(["git", "ls-remote", "backup", "HEAD"], capture_output=True, text=True, timeout=10)
        mb_hash = mb.stdout.split()[0][:7] if mb.stdout.strip() else "N/A"
        print(f"   Memory-Backup:{mb_hash}")
    except Exception:
        print("   Memory-Backup: N/A")

print("")
print("═══════════════════════════════════════════════")
print("   7 Günlük Görev Tamamlandı ✅")
print("═══════════════════════════════════════════════")
