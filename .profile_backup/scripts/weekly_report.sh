#!/bin/bash
# ReYMeN 7-Day Report - runs once after 7 days
# Summarizes all backups and checks

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
LOG_DIR="$HOME/AppData/Local/hermes/profiles/reymen/cron/output"

echo "═══════════════════════════════════════════════"
echo "   ReYMeN 7 Günlük Backup Raporu"
echo "   $TIMESTAMP"
echo "═══════════════════════════════════════════════"
echo ""

# Check hourly check count
HOURLY_COUNT=$(cat "$LOG_DIR/hourly_counter.txt" 2>/dev/null || echo "0")
echo "📊 Saatlik Kontrol"
echo "   Beklenen: 168  Gerçekleşen: $HOURLY_COUNT"
echo "   Durum: $([ "$HOURLY_COUNT" -ge 168 ] && echo '✅ TAM' || echo "⚠️  Eksik: $((168 - HOURLY_COUNT))")"

echo ""

# Check full backup count
FULL_COUNT=$(cat "$LOG_DIR/full_push_counter.txt" 2>/dev/null || echo "0")
echo "📦 Full Backup (03:00)"
echo "   Beklenen: 7  Gerçekleşen: $FULL_COUNT"
echo "   Durum: $([ "$FULL_COUNT" -ge 7 ] && echo '✅ TAM' || echo "⚠️  Eksik: $((7 - FULL_COUNT))")"

echo ""

# Check memory backup count
MEM_COUNT=$(cat "$LOG_DIR/memory_push_counter.txt" 2>/dev/null || echo "0")
echo "🧠 Memory Backup (00:30)"
echo "   Beklenen: 7  Gerçekleşen: $MEM_COUNT"
echo "   Durum: $([ "$MEM_COUNT" -ge 7 ] && echo '✅ TAM' || echo "⚠️  Eksik: $((7 - MEM_COUNT))")"

echo ""

# Last commit info
cd "$HOME/Desktop/Reymen Proje/hermes_projesi" 2>/dev/null
echo "🔗 Son Git Durumu"
echo "   Origin:     $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A') — $(git log -1 --format=%s 2>/dev/null || echo 'N/A')"
echo "   Full-Backup:$(git ls-remote full-backup HEAD 2>/dev/null | awk '{print substr($1,1,7)}')"
echo "   Memory-Backup:$(git ls-remote backup HEAD 2>/dev/null | awk '{print substr($1,1,7)}')"

echo ""
echo "═══════════════════════════════════════════════"
echo "   7 Günlük Görev Tamamlandı ✅"
echo "═══════════════════════════════════════════════"
