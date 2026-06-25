#!/usr/bin/env python3
"""
REYMEN SELF-HEAL LOOP — Otonom hata tespit + öneri + sandbox test döngüsü.

GÜVENLİK FELSEFESİ:
  - Otonom: tarama, kök neden analizi, düzeltme ÖNERİSİ, sandbox testi.
  - İnsan onayı: canlı dosyaya yazma. Onaysız üretim kodu DEĞİŞTİRİLMEZ.
  - Her şey loglanır, her düzeltme geri alınabilir (backup), her döngü sınırlı.

Çalıştırma:  python reymen_self_heal.py
Durdurma:    Ctrl+C  (graceful)
"""

import os
import re
import json
import time
import shutil
import hashlib
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# AYARLAR — kendine göre düzenle
# ─────────────────────────────────────────────
PROJE_KOK      = Path(__file__).parent.resolve()
LOG_DOSYALARI  = ["*.log"]
INTERVAL_DK    = 15
MAX_ITERASYON  = 0
BACKUP_DIR     = PROJE_KOK / "_self_heal_backups"
ONAY_KUYRUGU   = PROJE_KOK / "_pending_fixes.json"
SANDBOX_DIR    = PROJE_KOK / "_sandbox"
GORULMUS_HATA  = PROJE_KOK / "_seen_errors.json"

HATA_DESENLERI = [
    r"❌.*",
    r"\bERROR\b.*",
    r"Traceback \(most recent call last\)",
    r"Hafizada bulunamadi.*",
    r"drift_duzeltme.*",
    r"Exception.*",
    r"DEJENERASYON.*",
    r"HATA.*",
]

# ─────────────────────────────────────────────
# Logger
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SELF-HEAL] %(levelname)s → %(message)s",
    handlers=[
        logging.FileHandler(PROJE_KOK / "self_heal.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("self_heal")


# ─────────────────────────────────────────────
# 1. TESPİT — log dosyalarından hataları çek
# ─────────────────────────────────────────────
def hatalari_topla() -> list[dict]:
    bulunan = []
    taranmis = set()
    for desen in LOG_DOSYALARI:
        for log_path in PROJE_KOK.rglob(desen):
            if "_sandbox" in str(log_path) or "_self_heal" in str(log_path):
                continue
            if log_path in taranmis:
                continue
            taranmis.add(log_path)
            try:
                satirlar = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception as e:
                log.warning(f"Log okunamadi {log_path}: {e}")
                continue
            for i, satir in enumerate(satirlar):
                for hd in HATA_DESENLERI:
                    if re.search(hd, satir):
                        baglam = "\n".join(satirlar[max(0, i-1): i+3])
                        bulunan.append({
                            "dosya": str(log_path),
                            "satir_no": i + 1,
                            "hata": satir.strip()[:500],
                            "baglam": baglam[:1000],
                            "imza": hashlib.md5(satir.strip().encode()).hexdigest()[:10],
                        })
                        break
    return bulunan


# ─────────────────────────────────────────────
# 2. FİLTRE — daha önce görülen/işlenenleri ele
# ─────────────────────────────────────────────
def yeni_hatalar(hatalar: list[dict]) -> list[dict]:
    gorulmus = set()
    if GORULMUS_HATA.exists():
        try:
            gorulmus = set(json.loads(GORULMUS_HATA.read_text(encoding="utf-8")))
        except Exception:
            gorulmus = set()
    yeni = [h for h in hatalar if h["imza"] not in gorulmus]
    gorulmus.update(h["imza"] for h in hatalar)
    GORULMUS_HATA.write_text(json.dumps(list(gorulmus), indent=2), encoding="utf-8")
    return yeni


# ─────────────────────────────────────────────
# 3. KÖK NEDEN + DÜZELTME ÖNERİSİ
# ─────────────────────────────────────────────
def duzeltme_oner(hata: dict) -> dict:
    """
    Basit regex tabanlı kök neden analizi.
    Gerçek LLM entegrasyonu buraya bağlanabilir.
    """
    hata_str = hata["hata"]
    dosya = hata["dosya"]
    baglam = hata["baglam"]

    oneri = {
        "hedef_dosya": None,
        "eski_kod": "",
        "yeni_kod": "",
        "gerekce": "",
    }

    # Pattern 1: ImportError
    m = re.search(r"No module named '(\S+)'", hata_str)
    if m:
        modul = m.group(1)
        oneri["gerekce"] = f"Modul bulunamadi: {modul}"
        oneri["hedef_dosya"] = None
        log.info(f"[ANALIZ] ImportError: {modul}")
        return oneri

    # Pattern 2: CJK/Dejenerasyon
    if "DEJENERASYON" in hata_str or "CJK" in hata_str:
        oneri["gerekce"] = "Model dejenerasyonu tespit edildi — cikti_dogrulayici devrede"
        log.info(f"[ANALIZ] Dejenerasyon tespit")
        return oneri

    # Pattern 3: Cache miss
    if "Hafizada bulunamadi" in hata_str:
        oneri["gerekce"] = "Cache miss — normal durum, web araması tetiklenmeli"
        log.info(f"[ANALIZ] Cache miss — normal")
        return oneri

    # Pattern 4: Traceback — dosya/satır bilgisi çıkar
    m = re.search(r'File "([^"]+)", line (\d+)', baglam)
    if m:
        hedef_dosya = m.group(1)
        satir_no = int(m.group(2))
        oneri["hedef_dosya"] = hedef_dosya
        oneri["gerekce"] = f"Traceback: {hedef_dosya}:{satir_no}"
        log.info(f"[ANALIZ] Traceback: {hedef_dosya}:{satir_no}")
        return oneri

    oneri["gerekce"] = f"Otomatik analiz yapılamadı: {hata_str[:100]}"
    log.info(f"[ANALIZ] Bilinmeyen hata: {hata['imza']}")
    return oneri


# ─────────────────────────────────────────────
# 4. SANDBOX TEST
# ─────────────────────────────────────────────
def sandbox_test(oneri: dict) -> bool:
    hedef = oneri.get("hedef_dosya")
    if not hedef or not oneri.get("yeni_kod"):
        return False
    hedef_path = Path(hedef)
    if not hedef_path.exists():
        log.warning(f"Hedef dosya yok: {hedef}")
        return False

    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)
    shutil.copytree(PROJE_KOK, SANDBOX_DIR, ignore=shutil.ignore_patterns(
        "_sandbox", "_self_heal_backups", "__pycache__", ".git", "venv"))

    sb_hedef = SANDBOX_DIR / hedef_path.relative_to(PROJE_KOK) if hedef_path.is_absolute() else SANDBOX_DIR / hedef_path
    try:
        icerik = sb_hedef.read_text(encoding="utf-8")
        if oneri["eski_kod"] and oneri["eski_kod"] not in icerik:
            log.warning("Eski kod sandbox'ta bulunamadi")
            return False
        yeni_icerik = icerik.replace(oneri["eski_kod"], oneri["yeni_kod"], 1)
        sb_hedef.write_text(yeni_icerik, encoding="utf-8")

        sonuc = subprocess.run(
            ["python", "-m", "py_compile", str(sb_hedef)],
            capture_output=True, text=True, timeout=30)
        if sonuc.returncode != 0:
            log.warning(f"Sandbox derleme HATA: {sonuc.stderr}")
            return False

        log.info("✅ Sandbox testi geçti")
        return True
    except Exception as e:
        log.warning(f"Sandbox testi başarısız: {e}")
        return False


# ─────────────────────────────────────────────
# 5. ONAY KUYRUĞU
# ─────────────────────────────────────────────
def onaya_gonder(oneri: dict, hata: dict):
    kuyruk = []
    if ONAY_KUYRUGU.exists():
        try:
            kuyruk = json.loads(ONAY_KUYRUGU.read_text(encoding="utf-8"))
        except Exception:
            kuyruk = []
    kuyruk.append({
        "zaman": datetime.now().isoformat(),
        "hata": hata["hata"],
        "oneri": oneri,
        "sandbox_gecti": True,
        "durum": "ONAY_BEKLIYOR",
    })
    ONAY_KUYRUGU.write_text(json.dumps(kuyruk, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"📋 Onaya gönderildi → {ONAY_KUYRUGU}")


# ─────────────────────────────────────────────
# DÖNGÜ
# ─────────────────────────────────────────────
def dongu():
    BACKUP_DIR.mkdir(exist_ok=True)
    iterasyon = 0
    log.info(f"Self-heal başladı — her {INTERVAL_DK} dk. Durdurmak için Ctrl+C.")
    try:
        while True:
            iterasyon += 1
            log.info(f"───── Döngü #{iterasyon} ─────")
            hatalar = hatalari_topla()
            yeni = yeni_hatalar(hatalar)
            log.info(f"{len(hatalar)} hata bulundu, {len(yeni)} tanesi yeni")

            for h in yeni:
                oneri = duzeltme_oner(h)
                if sandbox_test(oneri):
                    onaya_gonder(oneri, h)
                else:
                    log.info(f"Otomatik düzeltilemedi → manuel: {h['imza']}")

            if MAX_ITERASYON and iterasyon >= MAX_ITERASYON:
                log.info("Max iterasyon — duruyor")
                break
            log.info(f"Sonraki döngü {INTERVAL_DK} dk sonra...")
            time.sleep(INTERVAL_DK * 60)
    except KeyboardInterrupt:
        log.info("Graceful kapanış (Ctrl+C)")


if __name__ == "__main__":
    dongu()
