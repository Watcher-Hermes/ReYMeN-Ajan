#!/bin/bash
# skills_sync_cron.sh — Skills -> DB senkronizasyon cron'u
cd /c/Users/marko/Desktop/Reymen\\ Proje/hermes_projesi/reymen/cereyan
echo "=== Skills Sync $(date) ==="
python3 skills_scan_to_db.py 2>&1
echo "=== Tamam $(date) ==="