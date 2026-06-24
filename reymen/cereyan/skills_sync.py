#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills_sync.py — reymen/cereyan/skills/ klasörünü OnceHafiza DB'sine senkronize eder.

Çalışma:
  1. skills/ altındaki tüm .md dosyalarını tara
  2. Her dosya için (hedef, kategori, icerik) belirle
  3. DB'de aynı hedef+kategori var mı kontrol et
     - YOKSA → INSERT (yeni)
     - VARSA, icerik farklıysa → UPDATE (güncel)
  4. Özet döndür: kaç yeni, kaç güncel, kaç atlandı

Kullanım:
  python3 reymen/cereyan/skills_sync.py
"""

import hashlib
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Yapılandırma ──────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.resolve()  # reymen/
SKILLS_DIR = ROOT / "cereyan" / "skills"
DB_PATH = ROOT / "cereyan" / ".ReYMeN" / "ogrenmeler.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("skills_sync")


def icerik_hash(icerik: str) -> str:
    """İçerik için MD5 hash — değişiklik kontrolü için."""
    return hashlib.md5(icerik.encode("utf-8")).hexdigest()


def kategori_bul(dosya_yolu: Path) -> str:
    """Dosya yolundan kategori çıkar.
    
    Örnek:
      Skiller/AI_ML/agents/file.md → "skill/agents"
      altin_ons_fiyati.md           → "skill"
      Skiller/Windows/file.md       → "skill/Windows"
    """
    rel = dosya_yolu.relative_to(SKILLS_DIR)
    parts = list(rel.parts[:-1])  # dosya adını çıkar
    
    # "Skiller/" prefix'ini temizle ve normalize et
    normalized = []
    for p in parts:
        p = p.replace("_", "/")
        normalized.append(p)
    
    if not normalized:
        return "skill"
    return "skill/" + "/".join(normalized)


def hedef_bul(dosya_yolu: Path) -> str:
    """Dosya adından hedef (başlık) çıkar - .md uzantısını kaldır."""
    return dosya_yolu.stem


def tarama_yap() -> dict:
    """
    Tüm .md dosyalarını tara ve DB ile karşılaştır.
    
    Returns:
        {"eklenen": int, "guncellenen": int, "atlanan": int, "toplam": int}
    """
    # DB'yi aç
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH), timeout=15)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    
    # Tablo yoksa oluştur
    con.executescript("""
        CREATE TABLE IF NOT EXISTS ogrenmeler (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            hedef           TEXT NOT NULL,
            kategori        TEXT NOT NULL DEFAULT 'genel',
            icerik          TEXT NOT NULL,
            guven_skoru     REAL NOT NULL DEFAULT 1.0,
            basari_sayisi   INTEGER NOT NULL DEFAULT 1,
            hata_sayisi     INTEGER NOT NULL DEFAULT 0,
            son_kullanim    TEXT NOT NULL DEFAULT (date('now')),
            gecerlilik_tarihi TEXT NOT NULL DEFAULT (date('now', '+180 days')),
            kaynak_url      TEXT DEFAULT NULL,
            olusturulma     TEXT NOT NULL DEFAULT (datetime('now')),
            guncelleme      TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_kategori ON ogrenmeler(kategori);
        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_hedef   ON ogrenmeler(hedef);
    """)
    
    # Mevcut kayıtları yükle: (hedef, kategori) → (id, icerik_hash)
    mevcut = {}
    try:
        cur = con.execute(
            "SELECT id, hedef, kategori, icerik FROM ogrenmeler"
        )
        for row in cur.fetchall():
            key = (row[1], row[2])  # (hedef, kategori)
            mevcut[key] = (row[0], icerik_hash(row[3]))
    except Exception as e:
        logger.error("DB okuma hatası: %s", e)
        mevcut = {}
    
    sayac = {"eklenen": 0, "guncellenen": 0, "atlanan": 0, "hata": 0}
    toplam_dosya = 0
    
    # Tüm .md dosyalarını tara (sembolik linkleri takip etme)
    md_dosyalar = sorted(SKILLS_DIR.rglob("*.md"))
    toplam_dosya = len(md_dosyalar)
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    bugun = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    for dosya in md_dosyalar:
        try:
            hedef = hedef_bul(dosya)
            kategori = kategori_bul(dosya)
            
            # İçeriği oku
            icerik = dosya.read_text(encoding="utf-8", errors="replace")
            yeni_hash = icerik_hash(icerik)
            
            key = (hedef, kategori)
            
            if key in mevcut:
                kayit_id, eski_hash = mevcut[key]
                if yeni_hash != eski_hash:
                    # İçerik değişmiş → güncelle
                    con.execute(
                        """UPDATE ogrenmeler SET
                            icerik = ?,
                            son_kullanim = ?,
                            guncelleme = ?
                        WHERE id = ?""",
                        (icerik, bugun, now, kayit_id),
                    )
                    sayac["guncellenen"] += 1
                    logger.debug("GÜNCELLENDİ: %s / %s", kategori, hedef[:50])
                else:
                    sayac["atlanan"] += 1  # aynı, atla
            else:
                # Yeni kayıt
                con.execute(
                    """INSERT INTO ogrenmeler
                       (hedef, kategori, icerik, guven_skoru, basari_sayisi,
                        son_kullanim, gecerlilik_tarihi, kaynak_url,
                        olusturulma, guncelleme)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (hedef, kategori, icerik, 0.7, 1,
                     bugun, bugun, "skill",
                     now, now),
                )
                sayac["eklenen"] += 1
                logger.debug("EKLENDİ: %s / %s", kategori, hedef[:50])
        
        except Exception as e:
            sayac["hata"] += 1
            logger.warning("HATA (%s): %s", dosya.name, e)
    
    con.commit()
    con.close()
    
    sayac["toplam"] = toplam_dosya
    return sayac


def ana():
    logger.info("=== Skills → OnceHafiza Sync Basliyor ===")
    logger.info("Klasor: %s", SKILLS_DIR)
    logger.info("DB: %s", DB_PATH)
    
    if not SKILLS_DIR.exists():
        logger.error("Klasor bulunamadi: %s", SKILLS_DIR)
        sys.exit(1)
    
    sonuc = tarama_yap()
    
    logger.info("=== Sync Tamam ===")
    logger.info("Toplam dosya: %d", sonuc["toplam"])
    logger.info("Yeni eklenen: %d", sonuc["eklenen"])
    logger.info("Guncellenen:  %d", sonuc["guncellenen"])
    logger.info("Atlanan (ayni): %d", sonuc["atlanan"])
    logger.info("Hata:          %d", sonuc["hata"])
    
    # Özet stdout'a yaz (cron log'u için)
    print(f"SKILLS_SYNC|{sonuc['toplam']}|{sonuc['eklenen']}|{sonuc['guncellenen']}|{sonuc['atlanan']}|{sonuc['hata']}")


if __name__ == "__main__":
    ana()
