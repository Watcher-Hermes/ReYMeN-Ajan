#!/bin/bash
# ============================================================
# ReYMeN Güncelleme Sistemi — ReYMeN Agent upstream sync (Hermes fork)
# ============================================================
# Kullanım:
#   bash .ReYMeN_sync.sh           — Durum göster
#   bash .ReYMeN_sync.sh --sync    — Güncellemeleri çek
#   bash .ReYMeN_sync.sh --diff    — Farkları göster
#   bash .ReYMeN_sync.sh --reset   — agent/ klasörünü upstream'den sıfırla
# ============================================================

UPSTREAM_REPO="https://github.com/nousresearch/hermes-agent.git"
UPSTREAM_BRANCH="main"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$REPO_DIR/.ReYMeN_sync_log.md"

# ReYMeN'e özel dosyalar (asla upstream'den üzerine yazılmaz)
REYMEN_PROTECTED=(
  "main.py" "beyin.py" "motor.py" "cli.py"
  "guardrails.py" "closed_learning_loop.py"
  "hata_cozucu.py" "tor_otomasyonu.py"
  "araclar_nisan.py" "nisan_yakala.py"
  "otonom_nisan_olusturucu.py" "akilli_yonlendirici.py"
  "cokus_raporlayici.py"
  "provider_router.py"
  "planlayici.py" "robust_execution.py"
  "insan_arayuzu.py" "vektorel_hafiza.py"
  "bounded_memory.py" "adaptif_ogrenme.py"
  "reflexion_motoru.py" "anayasa_denetci.py"
  "oz_yansima.py" "meta_prompt_optimizer.py"
  "oz_tutarlilik.py" "beceri_kutuphanesi.py"
  "ajan_suru.py"
)

# ReYMeN override dosyaları (kök = ReYMeN versiyonu, agent/ = backup)
# Sync sırasında agent/ güncellenir ama kök versiyonları KULLANILIR
REYMEN_OVERRIDES=(
  "account_usage.py" "bedrock_adapter.py"
  "codex_responses_adapter.py" "codex_runtime.py"
  "context_compressor.py" "context_references.py"
  "conversation_compression.py" "conversation_loop.py"
  "credential_persistence.py" "credential_pool.py"
  "display.py" "file_safety.py"
  "gemini_cloudcode_adapter.py" "insights.py"
  "iteration_budget.py" "lmstudio_reasoning.py"
  "memory_provider.py" "message_sanitization.py"
  "model_metadata.py" "moonshot_schema.py"
  "prompt_builder.py" "prompt_caching.py"
  "skill_utils.py" "stream_diag.py"
  "tool_executor.py" "tool_guardrails.py"
  "trajectory.py"
)

echo_color() {
  case "$1" in
    green) echo -e "\033[92m$2\033[0m" ;;
    red)   echo -e "\033[91m$2\033[0m" ;;
    blue)  echo -e "\033[94m$2\033[0m" ;;
    dim)   echo -e "\033[2m$2\033[0m" ;;
    *)     echo "$2" ;;
  esac
}

case "${1:-status}" in
  --sync)
    echo "## ReYMeN Güncelleme: $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # Upstream remote'u ekle (yoksa)
    if ! git -C "$REPO_DIR" remote | grep -q "upstream"; then
      git -C "$REPO_DIR" remote add upstream "$UPSTREAM_REPO"
      echo_color green "✓ Upstream remote eklendi: $UPSTREAM_REPO"
    fi

    # Upstream'den fetch et
    echo_color blue "📡 Upstream'den güncellemeler alınıyor..."
    if ! git -C "$REPO_DIR" fetch upstream "$UPSTREAM_BRANCH" 2>&1; then
      echo_color red "❌ Upstream fetch başarısız!"
      exit 1
    fi

    # agent/ klasöründeki değişiklikleri göster
    echo_color blue "📋 agent/ klasöründe değişen dosyalar:"
    git -C "$REPO_DIR" diff --name-only HEAD..upstream/"$UPSTREAM_BRANCH" -- agent/ | while read f; do
      echo_color dim "  • $f"
    done

    # Protected dosyaları koruyarak agent/ klasörünü güncelle
    echo_color blue "🔄 agent/ klasörü güncelleniyor..."
    git -C "$REPO_DIR" checkout upstream/"$UPSTREAM_BRANCH" -- agent/
    
    # Protected + Override dosyaları geri getir
    for f in "${REYMEN_PROTECTED[@]}" "${REYMEN_OVERRIDES[@]}"; do
      if [ -f "$REPO_DIR/$f" ]; then
        git -C "$REPO_DIR" checkout HEAD -- "$f" 2>/dev/null || true
      fi
    done

    NEW_HASH=$(git -C "$REPO_DIR" rev-parse --short upstream/"$UPSTREAM_BRANCH")
    echo "**Güncellendi:** upstream@$NEW_HASH" >> "$LOG_FILE"
    echo_color green "✅ Güncelleme tamam! (upstream@$NEW_HASH)"
    echo "" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    ;;

  --diff)
    # Farkları göster (agent/ klasörü)
    if ! git -C "$REPO_DIR" remote | grep -q "upstream"; then
      echo_color red "❌ Upstream remote bulunamadı. Önce: bash .ReYMeN_sync.sh --sync"
      exit 1
    fi
    git -C "$REPO_DIR" fetch upstream "$UPSTREAM_BRANCH" 2>/dev/null
    echo_color blue "📊 agent/ klasörü farkları:"
    git -C "$REPO_DIR" diff --stat HEAD..upstream/"$UPSTREAM_BRANCH" -- agent/
    ;;

  --reset)
    # agent/ klasörünü upstream'den sıfırla (tehlikeli!)
    echo_color red "⚠️  Bu işlem agent/ klasörünü tamamen sıfırlar!"
    echo_color red "   ReYMeN özel dosyalar korunacak."
    echo -n "   Devam etmek için 'EVET' yazın: "
    read onay
    if [ "$onay" != "EVET" ]; then
      echo_color red "❌ İptal edildi."
      exit 1
    fi
    git -C "$REPO_DIR" fetch upstream "$UPSTREAM_BRANCH"
    git -C "$REPO_DIR" checkout upstream/"$UPSTREAM_BRANCH" -- agent/
    for f in "${REYMEN_PROTECTED[@]}" "${REYMEN_OVERRIDES[@]}"; do
      if [ -f "$REPO_DIR/$f" ]; then
        git -C "$REPO_DIR" checkout HEAD -- "$f" 2>/dev/null || true
      fi
    done
    echo_color green "✅ agent/ sıfırlandı!"
    ;;

  *)
    # Durum göster
    echo_color blue "=== ReYMeN Güncelleme Durumu ==="
    echo "Repo: $REPO_DIR"
    echo ""
    
    if git -C "$REPO_DIR" remote | grep -q "upstream"; then
      git -C "$REPO_DIR" fetch upstream "$UPSTREAM_BRANCH" 2>/dev/null
      AHEAD=$(git -C "$REPO_DIR" rev-list --count HEAD..upstream/"$UPSTREAM_BRANCH" 2>/dev/null || echo "0")
      if [ "$AHEAD" -gt 0 ]; then
        echo_color red "📢 Upstream'de $AHEAD yeni commit var!"
        echo "   bash .ReYMeN_sync.sh --diff    # Farkları gör"
        echo "   bash .ReYMeN_sync.sh --sync    # Güncelle"
      else
        echo_color green "✓ Proje güncel"
      fi
    else
      echo_color dim "ℹ️  Upstream remote henüz eklenmemiş."
      echo "   bash .ReYMeN_sync.sh --sync  # İlk senkronizasyon"
    fi
    echo ""
    echo_color dim "🔒 ReYMeN özel: ${#REYMEN_PROTECTED[@]} dosya (korunuyor)"
    echo_color dim "🔄 Override: ${#REYMEN_OVERRIDES[@]} dosya (kök versiyonu kullanılır)"
    echo_color dim "📦 agent/ orijinal: $(ls "$REPO_DIR/agent/"*.py 2>/dev/null | wc -l) dosya"
    ;;
esac
