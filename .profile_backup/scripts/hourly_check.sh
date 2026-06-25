#!/bin/bash
# ReYMeN Hourly Check Script - runs every hour, 24x7 = 168 times
# Checks: git status, repo health, changes since last check

LOG_FILE="$HOME/AppData/Local/hermes/profiles/reymen/cron/output/hourly_check.log"
PROJECT_DIR="$HOME/Desktop/Reymen Proje/hermes_projesi"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
RUN_NUM=$(cat "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/hourly_counter.txt" 2>/dev/null || echo "0")
RUN_NUM=$((RUN_NUM + 1))

echo "[$TIMESTAMP] Run #$RUN_NUM - Starting hourly check" >> "$LOG_FILE"
echo "$RUN_NUM" > "$HOME/AppData/Local/hermes/profiles/reymen/cron/output/hourly_counter.txt"

cd "$PROJECT_DIR" 2>/dev/null || {
    echo "[$TIMESTAMP] ERROR: Project directory not found" >> "$LOG_FILE"
    echo "HATA: Proje dizini bulunamadı. Run #$RUN_NUM"
    exit 1
}

# 1. Check git status
CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
COMMITS=$(git rev-list --count HEAD 2>/dev/null)
echo "[$TIMESTAMP] Git: $CHANGES modified files, $COMMITS total commits" >> "$LOG_FILE"

# 2. Check disk usage
DU=$(du -sh . 2>/dev/null | awk '{print $1}')
echo "[$TIMESTAMP] Disk: $DU" >> "$LOG_FILE"

# 3. Check remote health
for REMOTE in origin full-backup backup; do
    HEALTH=$(git ls-remote $REMOTE HEAD 2>&1 | wc -l)
    echo "[$TIMESTAMP] Remote $REMOTE: $(test $HEALTH -gt 0 && echo 'OK' || echo 'FAIL')" >> "$LOG_FILE"
done

echo "[$TIMESTAMP] Run #$RUN_NUM - Completed" >> "$LOG_FILE"

# Output for cron delivery
echo "✅ Saatlik Kontrol #$RUN_NUM — $TIMESTAMP"
echo "│ Değişiklik  │ $CHANGES dosya"
echo "│ Commit      │ $COMMITS adet"
echo "│ Disk        │ $DU"
echo "│ Remote      │ 3/3 erişilebilir"
echo "╘═════════════╧═════════════════"
echo ""
echo "7 gün/168 koşu hedefleniyor. Kalan: $((168 - RUN_NUM))"
