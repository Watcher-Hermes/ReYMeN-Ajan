#!/bin/bash
# ReYMeN Daily Full Backup Push - runs at 03:00 daily (7 days)
# Pushes full project to hermes-full-backup + exports memory

LOG_FILE="$HOME/AppData/Local/hermes/profiles/reymen/cron/output/daily_full_push.log"
PROJECT_DIR="$HOME/Desktop/Reymen Proje/hermes_projesi"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
DAY_NUM=$(cat "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/full_push_counter.txt" 2>/dev/null || echo "0")
DAY_NUM=$((DAY_NUM + 1))

echo "[$TIMESTAMP] Day #$DAY_NUM - Starting full backup push" >> "$LOG_FILE"
echo "$DAY_NUM" > "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/full_push_counter.txt"

cd "$PROJECT_DIR" 2>/dev/null || {
    echo "[$TIMESTAMP] ERROR: Project directory not found" >> "$LOG_FILE"
    echo "HATA: Proje dizini bulunamadı. Day #$DAY_NUM"
    exit 1
}

# 1. Add all changes
git add -A 2>&1 >> "$LOG_FILE"

# 2. Commit
git commit -m "auto-backup $TIMESTAMP — full project" 2>> "$LOG_FILE"
COMMIT_RESULT=$?

# 3. Push to full-backup (main branch)
git push full-backup main 2>&1 >> "$LOG_FILE"
PUSH_RESULT=$?

# 4. Also backup profile state (memory)
cp -r "$HOME/AppData/Local/hermes/profiles/reymen" "$PROJECT_DIR/.profile_backup" 2>/dev/null
# Remove sensitive files from backup
rm -f "$PROJECT_DIR/.profile_backup/.env" 2>/dev/null

echo "[$TIMESTAMP] Day #$DAY_NUM - Commit: $COMMIT_RESULT, Push: $PUSH_RESULT" >> "$LOG_FILE"

# Output
echo "✅ Günlük Full Backup #$DAY_NUM/7 — $TIMESTAMP"
echo "│ Commit      │ $([ $COMMIT_RESULT -eq 0 ] && echo '✅ Yeni commit' || echo '⚠️  Değişiklik yok')"
echo "│ Push        │ $([ $PUSH_RESULT -eq 0 ] && echo '✅ Başarılı' || echo '❌ Başarısız')"
echo "│ Repo        │ Watcher-Hermes/hermes-full-backup"
echo "╘═════════════╧════════════════════════════"
echo ""
echo "Kalan gün: $((7 - DAY_NUM))"
