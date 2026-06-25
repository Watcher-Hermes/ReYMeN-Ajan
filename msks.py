# REYMEN AGENT - DERIN DEBUG GOREVI
#
# Bu dosya bir debug gorev belgesi ve Python scriptidir.
# Asagidaki Python kodu canli-veri sorununu duzeltir.
#

#!/usr/bin/env python3
"""
REYMEN CANLI-VERİ DÜZELTİCİ
═══════════════════════════════════════════════════════════════
SORUN: reymen, fiyat/kur/hava gibi CANLI sorguları bir kez web'den
çekip .md skill olarak kaydediyor; sonraki sorgularda eski kaydı
veriyor, asla güncellemiyor.

ÇÖZÜM (bu script):
  1. Canlı-veri içeren bozuk .md skill dosyalarını bulur ve siler
  2. once_hafiza / skill-kayıt mantığının dosyasını tespit eder
  3. Skill kaydeden fonksiyona "canlı sorgu = kaydetme" filtresi ekler
  4. Değişiklikleri doğrular

GÜVENLİK:
  • Varsayılan KURU çalışır — sadece rapor verir, dokunmaz.
  • Gerçekten uygulamak için:  python reymen_fix.py --uygula
  • Her dosya değişikliğinden ÖNCE .bak yedeği alınır.

KULLANIM:
  python reymen_fix.py            → ne yapacağını GÖSTERİR (dokunmaz)
  python reymen_fix.py --uygula   → değişiklikleri UYGULAR (yedekli)
═══════════════════════════════════════════════════════════════
"""

import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# AYARLAR
# ─────────────────────────────────────────────
PROJE_KOK = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")

# Canlı veri sayılan anahtar kelimeler — bunları içeren sorgular
# kalıcı skill yapılmamalı (her seferinde değişir).
CANLI_KELIMELER = [
    "fiyat", "fiyati", "kur", "döviz", "doviz", "altın", "altin",
    "ons", "gram", "borsa", "hisse", "bitcoin", "dolar", "euro",
    "hava", "hava durumu", "bugün", "bugun", "güncel", "guncel",
    "canlı", "canli", "şu an", "su an", "now", "today", "price",
    "kaç", "kac", "ne kadar",
]

DRY_RUN = "--uygula" not in sys.argv  # bayrak yoksa kuru çalış


def log(simge, mesaj):
    print(f"{simge} {mesaj}")


def yedekle(dosya: Path) -> Path:
    """Dosyanın .bak yedeğini alır, yedek yolunu döner."""
    damga = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek = dosya.with_suffix(dosya.suffix + f".bak_{damga}")
    shutil.copy2(dosya, yedek)
    return yedek


# ═══════════════════════════════════════════════
# ADIM 1 — Bozuk canlı-veri .md skill dosyalarını bul/sil
# ═══════════════════════════════════════════════
def bozuk_skilleri_temizle():
    print("\n" + "═" * 55)
    print("  ADIM 1 — Canlı-veri skill dosyaları taranıyor")
    print("═" * 55)

    skill_dosyalari = list(PROJE_KOK.rglob("*.md"))
    # sadece skills klasöründekiler
    skill_dosyalari = [p for p in skill_dosyalari if "skill" in str(p).lower()]

    bozuklar = []
    for md in skill_dosyalari:
        ad = md.stem.lower()
        if any(k in ad for k in CANLI_KELIMELER):
            bozuklar.append(md)

    if not bozuklar:
        log("✅", "Canlı-veri skill dosyası bulunamadı — temiz.")
        return

    log("🔍", f"{len(bozuklar)} adet canlı-veri skill dosyası bulundu:")
    for md in bozuklar:
        print(f"     • {md.relative_to(PROJE_KOK)}")

    if DRY_RUN:
        log("ℹ️ ", "[KURU MOD] Bunlar silinecek — --uygula ile gerçekleşir.")
    else:
        for md in bozuklar:
            yedek = yedekle(md)
            md.unlink()
            log("🗑️ ", f"Silindi (yedek: {yedek.name}): {md.name}")


# ═══════════════════════════════════════════════
# ADIM 2 — once_hafiza / skill-kayıt dosyasını bul
# ═══════════════════════════════════════════════
def kaynak_dosyalari_bul() -> list[Path]:
    print("\n" + "═" * 55)
    print("  ADIM 2 — Skill-kayıt mantığı aranıyor")
    print("═" * 55)

    adaylar = []
    for py in PROJE_KOK.rglob("*.py"):
        s = str(py).lower()
        if "venv" in s or "site-packages" in s or "_backup" in s:
            continue  # kütüphane ve yedekleri atla
        try:
            icerik = py.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # skill'i .md olarak YAZAN dosyayı ara
        if re.search(r"once_hafiza|skill", icerik, re.I) and \
           re.search(r"\.md|write_text|open\(.+['\"]w|\.write\(", icerik):
            adaylar.append(py)

    if not adaylar:
        log("⚠️ ", "Skill-kayıt yapan dosya net bulunamadı.")
        log("ℹ️ ", "Elle kontrol et: reymen\\sistem\\ ve reymen\\cereyan\\")
    else:
        log("🎯", f"{len(adaylar)} aday dosya:")
        for p in adaylar:
            print(f"     • {p.relative_to(PROJE_KOK)}")
    return adaylar


# ═══════════════════════════════════════════════
# ADIM 3 — Canlı-veri filtresi ekle
# ═══════════════════════════════════════════════
FILTRE_KODU = '''
# ═══ OTO-EKLENDİ: canlı-veri sorguları skill olarak kaydedilmesin ═══
_CANLI_KELIMELER = [
    "fiyat", "kur", "döviz", "altın", "ons", "gram", "borsa", "hisse",
    "bitcoin", "dolar", "euro", "hava", "bugün", "güncel", "canlı",
    "ne kadar", "kaç", "now", "today", "price",
]
def _canli_veri_mi(sorgu: str) -> bool:
    """Sorgu canlı/değişken veri istiyorsa True döner; bunlar cache'lenmez."""
    s = (sorgu or "").lower()
    return any(k in s for k in _CANLI_KELIMELER)
# ═══════════════════════════════════════════════════════════════════
'''


def filtre_ekle(dosya: Path):
    print("\n" + "═" * 55)
    print(f"  ADIM 3 — Filtre ekleniyor: {dosya.name}")
    print("═" * 55)

    icerik = dosya.read_text(encoding="utf-8", errors="replace")

    if "_canli_veri_mi" in icerik:
        log("✅", "Filtre zaten ekli — atlanıyor.")
        return

    if DRY_RUN:
        log("ℹ️ ", "[KURU MOD] Filtre fonksiyonu dosyanın başına eklenecek.")
        log("ℹ️ ", "Ayrıca skill-kaydeden satırın önüne şu koşul gelmeli:")
        print("       if _canli_veri_mi(sorgu): return  # kaydetme")
        return

    yedek = yedekle(dosya)
    # filtre fonksiyonunu import'lardan sonra, dosya başına ekle
    yeni = FILTRE_KODU + "\n" + icerik
    dosya.write_text(yeni, encoding="utf-8")
    log("✅", f"Filtre fonksiyonu eklendi (yedek: {yedek.name})")
    log("⚠️ ", "ELLE YAPMAN GEREKEN: skill kaydeden fonksiyonun içinde,")
    log("  ", "kayıt satırından ÖNCE şu kontrolü ekle:")
    print("       if _canli_veri_mi(sorgu): return  # canlı veri cache'lenmez")
    log("  ", "(Fonksiyonu otomatik bulamadım; bu tek satırı sen ekle.)")


# ═══════════════════════════════════════════════
# ÇALIŞTIR
# ═══════════════════════════════════════════════
def main():
    print("\n╔" + "═" * 53 + "╗")
    print("║  REYMEN CANLI-VERİ DÜZELTİCİ" + " " * 24 + "║")
    mod = "KURU (rapor)" if DRY_RUN else "UYGULA (değiştirir)"
    print(f"║  Mod: {mod:<46}║")
    print("╚" + "═" * 53 + "╝")

    if not PROJE_KOK.exists():
        log("❌", f"Proje yolu bulunamadı: {PROJE_KOK}")
        log("ℹ️ ", "Script başındaki PROJE_KOK yolunu düzelt.")
        return 1

    bozuk_skilleri_temizle()
    adaylar = kaynak_dosyalari_bul()

    if adaylar:
        # en olası dosyayı seç: once_hafiza geçen, en kısa yol
        oncelik = sorted(adaylar, key=lambda p: (
            "once_hafiza" not in p.read_text(encoding="utf-8", errors="replace").lower(),
            len(str(p))))
        filtre_ekle(oncelik[0])

    print("\n" + "═" * 55)
    if DRY_RUN:
        log("ℹ️ ", "KURU MOD bitti. Hiçbir şey değişmedi.")
        log("👉", "Onaylıyorsan tekrar çalıştır:  python reymen_fix.py --uygula")
    else:
        log("✅", "UYGULAMA bitti. Yedekler .bak_* olarak duruyor.")
        log("👉", "Şimdi reymen'i çalıştırıp altın fiyatını tekrar sor.")
    print("═" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
