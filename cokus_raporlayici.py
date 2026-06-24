# -*- coding: utf-8 -*-
"""cokus_raporlayici root shim — patch.object ile test edilebilir."""
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Bu modül seviyesi değişken test sırasında patch.object ile override edilebilir
RAPOR_DIZINI = Path(__file__).parent / ".ReYMeN" / "cokus_raporlari"

# Inner modülden diğer exportlar
from reymen.cereyan.cokus_raporlayici import *  # noqa: F401, F403


def cokus_raporu_uret(
    gorev: str,
    deneme_sayisi: int,
    hata_gecmisi: List[str],
    denenen_ajanlar: List[str],
    tiklanma_nedeni: Optional[str] = None,
) -> str:
    """Çöküş raporu oluştur — RAPOR_DIZINI bu modülden okunur (patch edilebilir)."""
    rapor_dizin = RAPOR_DIZINI
    rapor_dizin.mkdir(parents=True, exist_ok=True)

    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dosya_adi = f"cokus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    dosya_yolu = rapor_dizin / dosya_adi

    if not tiklanma_nedeni and hata_gecmisi:
        tiklanma_nedeni = hata_gecmisi[-1]
    elif not tiklanma_nedeni:
        tiklanma_nedeni = "Belirlenemeyen sistem kesintisi."

    hata_metni = "\n".join(f"  [{i+1}] {log}" for i, log in enumerate(hata_gecmisi))
    if not hata_metni:
        hata_metni = "  (Hata kaydi yok)"

    ajan_metni = ", ".join(sorted(set(denenen_ajanlar))) if denenen_ajanlar else "Henuz ajan secilmemisti."

    rapor = f"""
============================================================
🚨 [OTONOM SISTEM COKUS / TAHLIYE RAPORU] 🚨
============================================================
Kritik Zaman Dilimi    : {tarih}
Basarisiz Olunan Gorev : {gorev}
Toplam Tuketilen Dongu : {deneme_sayisi} Tur

------------------------------------------------------------
🔍 [KRONOLOJIK HATA VE ADAPTASYON GECMISI]
------------------------------------------------------------
{hata_metni}

------------------------------------------------------------
🧠 [GOREV SURESINCE DENENEN AJANLAR]
------------------------------------------------------------
{ajan_metni}

------------------------------------------------------------
⚠️  [OLUMCUL KILITLENME NOKTASI (KOK NEDEN)]
------------------------------------------------------------
{tiklanma_nedeni}

============================================================
🚨 KULLANICI ACIL MUDAHALE VE GOREV DEVRİ PROTOKOLU
============================================================
  1. Yukaridaki verileri inceleyin
  2. Bir COZUM ONERISI hazirlayin
  3. Cozum onerisini sisteme YENI BIR GOREV olarak iletin
============================================================
""".strip()

    with open(str(dosya_yolu), "w", encoding="utf-8") as f:
        f.write(rapor)

    return rapor
