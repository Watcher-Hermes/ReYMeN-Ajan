#!/bin/bash
# ReYMeN Daily Memory Backup Push - runs at 00:30 daily (7 days)
# Pushes latest state to hermes-memory-backup

LOG_FILE="$HOME/AppData/Local/hermes/profiles/reymen/cron/output/daily_memory_push.log"
PROJECT_DIR="$HOME/Desktop/Reymen Proje/hermes_projesi"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
DAY_NUM=$(cat "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/memory_push_counter.txt" 2>/dev/null || echo "0")
DAY_NUM=$((DAY_NUM + 1))

echo "[$TIMESTAMP] Day #$DAY_NUM - Starting memory backup push" >> "$LOG_FILE"
echo "$DAY_NUM" > "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/memory_push_counter.txt"

cd "$PROJECT_DIR" 2>/dev/null || {
    echo "[$TIMESTAMP] ERROR: Project directory not found" >> "$LOG_FILE"
    echo "HATA: Proje dizini bulunamadı. Day #$DAY_NUM"
    exit 1
}

# 1. Sync profile state to project (memory data)
mkdir -p "$PROJECT_DIR/.profile_snapshot" 2>/dev/null
cp "$HOME/AppData/Local/hermes/profiles/reymen/auth.json" "$PROJECT_DIR/.profile_snapshot/" 2>/dev/null
cp "$HOME/AppData/Local/hermes/profiles/reymen/config.yaml" "$PROJECT_DIR/.profile_snapshot/" 2>/dev/null

# 2. Add memory-related files
git add .ReYMeN/ .profile_snapshot/ decisions.md AGENTS.md 2>&1 >> "$LOG_FILE"

# 3. Commit
git commit -m "memory-backup $TIMESTAMP — state + decisions" 2>> "$LOG_FILE"
COMMIT_RESULT=$?

# 4. Push to backup (memory-backup, master branch)
git push backup master 2>&1 >> "$LOG_FILE"
PUSH_RESULT=$?

echo "[$TIMESTAMP] Day #$DAY_NUM - Commit: $COMMIT_RESULT, Push: $PUSH_RESULT" >> "$LOG_FILE"

# Output
echo "✅ Günlük Memory Backup #$DAY_NUM/7 — $TIMESTAMP"
echo "│ Commit      │ $([ $COMMIT_RESULT -eq 0 ] && echo '✅ Yeni commit' || echo '⚠️  Değişiklik yok')"
echo "│ Push        │ $([ $PUSH_RESULT -eq 0 ] && echo '✅ Başarılı' || echo '❌ Başarısız')"
echo "│ Repo        │ Watcher-Hermes/hermes-memory-backup"
echo "╘═════════════╧════════════════════════════"
echo ""
echo "Kalan gün: $((7 - DAY_NUM))"
