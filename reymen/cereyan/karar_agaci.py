# -*- coding: utf-8 -*-
"""
karar_agaci.py — Karar ağacı ve stratejik seçim mekanizması.

Amaç:
- Görev geldiğinde en doğru aksiyonu belirlemek için karar ağacı
- Farklı senaryolar için önceden tanımlı karar dalları
- Öğrenme verilerinden otomatik karar ağacı güncelleme

Kullanım:
    from reymen.cereyan.karar_agaci import KararAgaci
    ka = KararAgaci()
    karar = ka.değerlendir(hedef="port taramasi", kategori="kali/network")
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent.parent.resolve()
KARAR_DB = ROOT / "reymen" / "cereyan" / ".ReYMeN" / "karar.db"
OGRENME_DB = ROOT / "reymen" / "hafiza" / "ogrenme.db"


@dataclass
class KararKurali:
    """Tek bir karar kuralı."""
    id: int = 0
    tetikleyici: str = ""         # Regex/anahtar kelime
    kategori: str = ""             # Hedef kategori
    aksiyon: str = ""              # Yapılacak işlem
    guven_esigi: float = 0.5      # Minimum güven
    oncelik: int = 5               # 1=en yüksek, 10=en düşük
    aktif: bool = True
    olusturulma: str = ""
    aciklama: str = ""


class KararAgaci:
    """Ana karar ağacı motoru."""

    # Varsayılan kurallar (DB boşsa yüklenir)
    VARSAYILAN_KURALLAR = [
        KararKurali(
            tetikleyici=r"(port|nmap|servis|tarama|ag)",
            kategori="kali/network/nmap",
            aksiyon="nmap_taramasi_baslat",
            guven_esigi=0.4, oncelik=3,
            aciklama="Port taramasi icin nmap kullan",
        ),
        KararKurali(
            tetikleyici=r"(sql|injection|xss|web.*güvenlik)",
            kategori="kali/web",
            aksiyon="web_guvenlik_tarama",
            guven_esigi=0.5, oncelik=4,
            aciklama="Web guvenlik taramasi baslat",
        ),
        KararKurali(
            tetikleyici=r"(hafiza|kaydet|ogren|hatirla)",
            kategori="cross-platform/hafiza",
            aksiyon="once_hafiza_dene",
            guven_esigi=0.3, oncelik=2,
            aciklama="Once hafizaya basvur",
        ),
        KararKurali(
            tetikleyici=r"(guncelle|yenile|upgrade|update)",
            kategori="cross-platform/bakim",
            aksiyon="guncelleme_baslat",
            guven_esigi=0.6, oncelik=6,
            aciklama="Sistem guncellemesi baslat",
        ),
        KararKurali(
            tetikleyici=r"(dron|drone|px4|uav|iha)",
            kategori="dron",
            aksiyon="dron_kontrol_baslat",
            guven_esigi=0.5, oncelik=5,
            aciklama="Dron kontrol modulunu aktif et",
        ),
        KararKurali(
            tetikleyici=r"(test|calistir|run|pytest|dogrula)",
            kategori="cross-platform/test",
            aksiyon="test_suite_calistir",
            guven_esigi=0.5, oncelik=5,
            aciklama="Test suite'ini calistir",
        ),
        KararKurali(
            tetikleyici=r"(yardim|help|nasil|ne.*yap)",
            kategori="cross-platform/yardim",
            aksiyon="yardim_goster",
            guven_esigi=0.2, oncelik=1,
            aciklama="Yardim menusu goster",
        ),
        KararKurali(
            tetikleyici=r"(git|github|push|commit|yukle|pull|branch|repo|depo)",
            kategori="developer/versiyon-kontrol",
            aksiyon="git_islemi_baslat",
            guven_esigi=0.5, oncelik=4,
            aciklama="Git/GitHub versiyon kontrol islemi yap",
        ),
    ]

    def __init__(self, karar_db: str | Path = KARAR_DB):
        self.karar_db = str(karar_db)
        self._db_kur()
        if self._kural_sayisi() == 0:
            self._varsayilan_kurallari_yukle()

    def _db_kur(self) -> None:
        os.makedirs(Path(self.karar_db).parent, exist_ok=True)
        con = sqlite3.connect(self.karar_db)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript("""
            CREATE TABLE IF NOT EXISTS karar_kurallari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tetikleyici TEXT NOT NULL,
                kategori TEXT DEFAULT '',
                aksiyon TEXT NOT NULL,
                guven_esigi REAL DEFAULT 0.5,
                oncelik INTEGER DEFAULT 5,
                aktif INTEGER DEFAULT 1,
                olusturulma TEXT DEFAULT (datetime('now')),
                aciklama TEXT DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_kural_kategori ON karar_kurallari(kategori);
        """)
        con.commit()
        con.close()

    def _kural_sayisi(self) -> int:
        con = sqlite3.connect(self.karar_db)
        count = con.execute("SELECT COUNT(*) FROM karar_kurallari").fetchone()[0]
        con.close()
        return count

    def _varsayilan_kurallari_yukle(self) -> None:
        con = sqlite3.connect(self.karar_db)
        for k in self.VARSAYILAN_KURALLAR:
            con.execute(
                "INSERT INTO karar_kurallari "
                "(tetikleyici, kategori, aksiyon, guven_esigi, oncelik, aciklama) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (k.tetikleyici, k.kategori, k.aksiyon,
                 k.guven_esigi, k.oncelik, k.aciklama),
            )
        con.commit()
        con.close()
        logger.info("[KararAgaci] %d varsayilan kural yuklendi",
                     len(self.VARSAYILAN_KURALLAR))

    def degerlendir(
        self,
        hedef: str,
        kategori: str = "",
        hafiza_guveni: float = 0.0,
    ) -> dict[str, Any]:
        """Hedefe en uygun kararı bul.

        Args:
            hedef: Görev/hedef metni.
            kategori: Opsiyonel kategori filtresi.
            hafiza_guveni: OnceHafiza'dan gelen güven skoru (0-1).

        Returns:
            {"karar": str|None, "kural": dict|None,
             "eslesme": str, "guven_esigi": float,
             "kaynak": str}
        """
        basla = time.time()
        hedef_lower = hedef.lower()

        con = sqlite3.connect(self.karar_db)
        cur = con.execute(
            "SELECT id, tetikleyici, kategori, aksiyon, guven_esigi, "
            "       oncelik, aktif, aciklama "
            "FROM karar_kurallari WHERE aktif = 1 "
            "ORDER BY oncelik ASC, guven_esigi DESC"
        )

        en_iyi_kural = None
        en_iyi_eslesme = ""

        for row in cur.fetchall():
            kural = {
                "id": row[0], "tetikleyici": row[1], "kategori": row[2],
                "aksiyon": row[3], "guven_esigi": row[4], "oncelik": row[5],
                "aktif": bool(row[6]), "aciklama": row[7],
            }

            # Regex eslestirme
            try:
                if re.search(kural["tetikleyici"], hedef_lower):
                    # Kategori filtresi varsa
                    if kategori and kural["kategori"]:
                        if kategori not in kural["kategori"]:
                            continue

                    # Guven esigi kontrol (OnceHafiza'dan gelen guven varsa)
                    eslesme_guven = max(hafiza_guveni, 0.5)
                    if eslesme_guven >= kural["guven_esigi"]:
                        en_iyi_kural = kural
                        en_iyi_eslesme = kural["tetikleyici"]
                        break  # oncelik sirali, ilk eslesen en iyisi

            except re.error:
                continue

        con.close()

        if en_iyi_kural:
            sonuc = {
                "karar": en_iyi_kural["aksiyon"],
                "kural": en_iyi_kural,
                "eslesme": en_iyi_eslesme,
                "guven_esigi": en_iyi_kural["guven_esigi"],
                "kaynak": "karar_agaci",
                "sure": round(time.time() - basla, 3),
            }
        else:
            sonuc = {
                "karar": None,
                "kural": None,
                "eslesme": "",
                "guven_esigi": 0.0,
                "kaynak": "karar_agaci",
                "sure": round(time.time() - basla, 3),
            }

        return sonuc

    def kural_ekle(
        self,
        tetikleyici: str,
        aksiyon: str,
        kategori: str = "",
        guven_esigi: float = 0.5,
        oncelik: int = 5,
        aciklama: str = "",
    ) -> int:
        """Yeni kural ekle. Dönen: kural ID'si."""
        con = sqlite3.connect(self.karar_db)
        con.execute(
            "INSERT INTO karar_kurallari "
            "(tetikleyici, kategori, aksiyon, guven_esigi, oncelik, aciklama) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (tetikleyici, kategori, aksiyon, guven_esigi, oncelik, aciklama),
        )
        con.commit()
        kural_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.close()
        logger.info("[KararAgaci] Kural eklendi: id=%d, tetikleyici=%s",
                     kural_id, tetikleyici)
        return kural_id

    def ogrenmelerden_kural_olustur(self, limit: int = 20) -> int:
        """OnceHafiza ogrenmeler DB'sinden basarili kayitlari kurala cevir.

        Returns:
            Eklenen kural sayisi.
        """
        try:
            con = sqlite3.connect(OGRENME_DB)
            rows = con.execute(
                "SELECT hedef, kategori FROM ogrenmeler "
                "WHERE basari_sayisi >= 3 AND guven_skoru >= 0.7 "
                "ORDER BY guven_skoru DESC LIMIT ?",
                (limit,),
            ).fetchall()
            con.close()
        except Exception:
            return 0

        eklenen = 0
        for hedef, kategori in rows:
            # Hedeften anahtar kelime uret
            kelimeler = re.findall(r"[a-zA-Z_]+", hedef)
            if len(kelimeler) >= 2:
                tetikleyici = "|".join(kelimeler[:3])
                try:
                    self.kural_ekle(
                        tetikleyici=tetikleyici,
                        aksiyon=f"otomatik_{kelimeler[0]}",
                        kategori=kategori or "",
                        guven_esigi=0.6,
                        oncelik=7,
                        aciklama=f"OnceHafiza'dan otomatik: {hedef[:50]}",
                    )
                    eklenen += 1
                except Exception as e:
                    logger.warning("[KararAgaci] Kural ekleme hatasi: %s", e)

        logger.info("[KararAgaci] %d kural OnceHafiza'dan olusturuldu", eklenen)
        return eklenen


# ── Test ──
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ka = KararAgaci()

    testler = [
        "port taramasi yap",
        "sql injection test",
        "hafizaya kaydet su bilgiyi",
        "dron ucur",
        "testleri calistir",
        "rastgele metin",
    ]
    for t in testler:
        karar = ka.degerlendir(t)
        print(f"  {t:30s} → {karar['karar'] or 'ESLESME_YOK':30s} "
              f"(guven_esigi={karar['guven_esigi']})")
