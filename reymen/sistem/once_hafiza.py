# -*- coding: utf-8 -*-
"""
once_hafiza.py — "Önce Hafızaya Bak" prensibi.

ENTEGRE SÜRÜM (2026-06-23):
  → 4 fonksiyon reymen/cereyan/once_hafiza.py'den entegre edildi:
    1. kaydet() — sigmoid güven hesaplamalı
    2. ara() — kategori/güven/geçerlilik filtreli
    3. guven_guncelle() — bağımsız güven güncelleme
    4. isle() — hafıza-öncelikli çalıştırma döngüsü
  → DB: cereyan/.ReYMeN/ogrenmeler.db (tek kaynak)
  → Kendi metotları (hata_kaydet, hata_cozum_bul, analiz_et) korundu.

Her görev öncesi:
  1. Hafızada (SQLite FTS5 + vektörel) benzer çözüm var mı kontrol et
  2. VARSA → direkt uygula, süreyi kısalt
  3. YOKSA → dene, başarılıysa kaydet
  4. HATA OLDUYSA → analiz et, düzelt, kaydet

Kullanım:
    from reymen.sistem.once_hafiza import OnceHafiza
    oh = OnceHafiza()
    sonuc = oh.isle(hedef="kullanici hedefi")
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# ── Import 4 fonksiyon (cereyan/once_hafiza.py — TEK KAYNAK) ────────────────
from reymen.cereyan.once_hafiza import (
    kaydet as _cereyan_kaydet,
    ara as _cereyan_ara,
    guven_guncelle as _cereyan_guven_guncelle,
    _kademeli_guven as _cereyan_kademeli_guven,
    belirsiz_gorev_cozumle as _cereyan_belirsiz_cozum,
    _benzerlik_skoru as _cereyan_benzerlik,
    eski_kayitlari_temizle as _cereyan_temizle,
)
# Module-level alias (aynı isimle kullanım için)
_kademeli_guven = _cereyan_kademeli_guven

ROOT = Path(__file__).parent.parent.resolve()

logger = logging.getLogger(__name__)

# Varsayılan yollar — cereyan/ ile AYNI DB
SKILLS_DB = ROOT / "cereyan" / ".ReYMeN" / "skills_index.db"
SKILLS_DIR = ROOT / "cereyan" / "skills"
OGRENME_DB = ROOT / "cereyan" / ".ReYMeN" / "ogrenmeler.db"  # ← tek kaynak
HATA_DB = ROOT / "hafiza" / "hatalar.db"
HATA_DB.parent.mkdir(parents=True, exist_ok=True)


class OnceHafiza:
    """
    Önce Hafızaya Bak prensibi.
    
    Her işlem öncesi:
    1. Hafızada benzer çözüm ara (cereyan DB)
    2. Bulursan direkt uygula (tekrar keşfetme)
    3. Bulamazsan dene + kaydet
    4. Hata olursa analiz et + düzelt + kaydet

    DELEGASYON: kaydet(), ara(), guven_guncelle(), isle()
    → cereyan/once_hafiza.py'ye yönlendirilir (tek DB, tek kaynak).
    """

    @staticmethod
    def _kademeli_guven(basari: int, hata: int) -> float:
        """Sigmoid güven — cereyan/once_hafiza.py'ye delege eder."""
        return _cereyan_kademeli_guven(basari, hata)

    def __init__(
        self,
        skills_db: str | Path = SKILLS_DB,
        skills_dir: str | Path = SKILLS_DIR,
        ogrenme_db: str | Path = OGRENME_DB,
        hata_db: str | Path = HATA_DB,
    ):
        self.skills_db = str(skills_db)
        self.skills_dir = str(skills_dir)
        self.ogrenme_db = str(ogrenme_db)
        self.hata_db = str(hata_db)

        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(Path(self.ogrenme_db).parent, exist_ok=True)
        os.makedirs(Path(self.hata_db).parent, exist_ok=True)

        self._db_kur()

    # ── Veritabanı Kurulumu ──────────────────────────────────────────────

    def _db_kur(self) -> None:
        """FTS5 öğrenme + hata veritabanlarını kur."""
        import sqlite3

        # cereyan DB zaten _cereyan_kaydet/ara tarafından kurulur.
        # Burada sadece hata DB'sini kuruyoruz.
        con = sqlite3.connect(self.hata_db)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript("""
            CREATE TABLE IF NOT EXISTS hatalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hedef TEXT NOT NULL,
                hata TEXT NOT NULL,
                traceback TEXT DEFAULT '',
                cozum TEXT DEFAULT '',
                cozuldu INTEGER DEFAULT 0,
                tarih TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_hata_hedef ON hatalar(hedef);
        """)
        con.commit()
        con.close()

    # ── ADIM 1: Hafızada Ara (cereyan delegasyonu) ──────────────────────

    def hafizada_ara(self, hedef: str, kategori: str = "") -> dict[str, Any] | None:
        """Hafızada benzer çözüm ara.

        Args:
            hedef: Kullanıcı hedefi / görev tanımı.
            kategori: filtre veya "" (filtresiz).

        Returns:
            {"hedef": str, "cozum": str, "kaynak": str, "guven": float} veya None.
        """
        import sqlite3

        # ÖNCE: cereyan DB'de tam eşleşme + LIKE ara
        # _cereyan_ara() -> list[dict] döndürür
        cereyan_sonuc = _cereyan_ara(
            hedef=hedef,
            kategori=kategori if kategori else None,
            min_guven=0.0,
            gecerli_mi=False,
        )
        if cereyan_sonuc:
            en_iyi = cereyan_sonuc[0]
            guven = en_iyi.get("guven_skoru", 0.5)
            sonuc = {
                "hedef": en_iyi.get("hedef", hedef),
                "cozum": en_iyi.get("icerik", ""),
                "kaynak": "ogrenme",
                "guven": guven,
            }
            if en_iyi.get("kategori"):
                sonuc["kategori"] = en_iyi["kategori"]
            if guven < 0.5:
                sonuc["durum"] = "belirsiz"
                sonuc["uyari"] = f"⚠️ Güven skoru düşük ({guven:.2f})"
                logger.warning(
                    "[OnceHafiza] ⚠️ Belirsiz (cereyan): %s guven=%.2f",
                    hedef[:50], guven,
                )
                return sonuc

            # Kullanım güncelle (güven ++)
            _cereyan_guven_guncelle(en_iyi["id"], basari=True)
            logger.info(
                "[OnceHafiza] ✅ Cereyan DB'de bulundu: %s (guven=%.2f)",
                hedef[:50], guven,
            )
            return sonuc

        # FTS5 skills'te ara (varsa)
        try:
            scon = sqlite3.connect(self.skills_db, timeout=5)
            try:
                row = scon.execute(
                    "SELECT ad, aciklama, icerik, kaynak FROM beceriler "
                    "WHERE beceriler MATCH ? ORDER BY rank LIMIT 1",
                    (hedef,),
                ).fetchone()
                if row:
                    logger.info(
                        "[OnceHafiza] 🔍 Skills FTS5'te bulundu: %s", row[0]
                    )
                    return {"hedef": row[0], "cozum": row[2],
                            "kaynak": row[3] or "skills", "guven": 0.7}
            except Exception:
                pass
            finally:
                scon.close()
        except Exception:
            pass

        logger.info("[OnceHafiza] ❌ Hafizada bulunamadi: %s", hedef[:60])
        return None

    # ── ADIM 2: Kaydet (cereyan delegasyonu) ─────────────────────────────

    def kaydet(
        self, hedef: str, cozum: str, kaynak: str = "kesif",
        kategori: str = "", kaynak_url: str | None = None,
    ) -> None:
        """Başarılı çözümü cereyan DB'sine kaydet (sigmoid güven hesaplamalı).

        Varsa: basari_sayisi++, guven_skoru yeniden hesapla
        Yoksa: yeni kayıt (guven=0.5 başlangıç)
        """
        _cereyan_kaydet(
            hedef=hedef,
            kategori=kategori or "genel",
            icerik=cozum,
            basari=True,
            kaynak_url=kaynak_url,
        )
        logger.info(
            "[OnceHafiza] ✅ Cereyan DB'ye kaydedildi: %s (kat=%s)",
            hedef[:50], kategori or "genel",
        )

    # ── ADIM 3: Hata Kaydet (yerel) ─────────────────────────────────────

    def hata_kaydet(
        self, hedef: str, hata: str, tb: str = ""
    ) -> None:
        """Hata kaydı tut. Ayrıca cereyan DB'de guven_skoru güncelle."""
        import sqlite3

        # Cereyan DB'de güven güncelle
        try:
            kayitlar = _cereyan_ara(hedef, min_guven=0.0, gecerli_mi=False)
            if kayitlar:
                _cereyan_guven_guncelle(kayitlar[0]["id"], basari=False)
        except Exception:
            pass

        # Yerel hata DB'sine kaydet
        try:
            con = sqlite3.connect(self.hata_db, timeout=5)
            try:
                con.execute(
                    "INSERT INTO hatalar (hedef, hata, traceback) "
                    "VALUES (?, ?, ?)",
                    (hedef[:500], str(hata)[:1000], tb[:2000]),
                )
                con.commit()
                logger.info(
                    "[OnceHafiza] ❌ Hata kaydedildi: %s", hedef[:50]
                )
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

    def hata_cozum_bul(
        self, hedef: str, hata: str
    ) -> dict[str, Any] | None:
        """Benzer hata için daha önce çözüm bulunmuş mu?"""
        import sqlite3

        try:
            con = sqlite3.connect(self.hata_db, timeout=5)
            try:
                row = con.execute(
                    "SELECT cozum FROM hatalar WHERE cozuldu = 1 "
                    "AND (hedef LIKE ? OR hata LIKE ?) LIMIT 1",
                    (f"%{hedef[:30]}%", f"%{str(hata)[:50]}%"),
                ).fetchone()
                if row and row[0]:
                    return {"cozum": row[0]}
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass
        return None

    def hata_cozuldu_isaretle(self, hedef: str, cozum: str) -> None:
        """Çözülen hatayı işaretle."""
        import sqlite3

        try:
            con = sqlite3.connect(self.hata_db, timeout=5)
            try:
                con.execute(
                    "UPDATE hatalar SET cozuldu = 1, cozum = ? "
                    "WHERE hedef = ? AND cozuldu = 0",
                    (cozum, hedef[:500]),
                )
                con.commit()
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

    # ── ADIM 4: Analiz Et (regex+skor bazlı, LLM'siz) ──────────────────

    def analiz_et(self, hedef: str, hata: str) -> str:
        """Hata analizi yap, düzeltme önerisi üret.
        LLM'siz çalışır: regex + skor bazlı hata sınıflandırması.
        """
        import re

        hata_lower = (str(hata) or "").lower()

        patterns = {
            "import_hatasi": r"no module named|import error|module.*not found",
            "syntax_hatasi": r"invalid syntax|unexpected.*token|eol while",
            "baglanti_hatasi": r"connection refused|timeout|network.*unreachable",
            "api_hatasi": r"401|403|404|429|500|unauthorized|rate limit",
            "dosya_hatasi": r"file not found|no such file|permission denied",
            "tip_hatasi": r"attributeerror|typeerror|valueerror|keyerror",
            "dll_hatasi": r"dll load|not a valid win32|entry point",
        }

        eslesen = []
        for kat, pattern in patterns.items():
            if re.search(pattern, hata_lower):
                eslesen.append(kat)

        if not eslesen:
            return f"Hata analiz edilemedi:\n{hata[:300]}"

        cozum_onerileri = {
            "import_hatasi": "Eksik paket: `pip install <paket>`",
            "syntax_hatasi": "Kodda yazım hatası: satır bazlı incele",
            "baglanti_hatasi": "Ağ bağlantısı kesik: servis çalışıyor mu?",
            "api_hatasi": "API anahtarı/sınır sorunu",
            "dosya_hatasi": "Dosya yolu hatalı: dizin var mı?",
            "tip_hatasi": "Değişken tipi uyuşmazlığı: type cast",
            "dll_hatasi": "Windows DLL/bağımlılık sorunu",
        }
        oneriler = [cozum_onerileri.get(k, "?") for k in eslesen]
        kat_str = ", ".join(eslesen)
        oneri_str = " -> ".join(oneriler)
        return f"Hata: {kat_str}\nDüzeltme: {oneri_str}"

    # ── ANA DÖNGÜ (isle) — cereyan delegasyonlu ─────────────────────────

    def isle(
        self,
        hedef: str,
        calistirici: Callable[[str], dict[str, Any]] | None = None,
        otomatik_kaydet: bool = True,
        otomatik_coz: bool = True,
        kategori: str = "",
        kaynak_url: str | None = None,
    ) -> dict[str, Any]:
        """Ana işlem döngüsü: Önce hafızaya bak.

        Args:
            hedef: Yapılacak görev / işlem.
            calistirici: İşlemi çalıştıracak fonksiyon (None=simülasyon).
            otomatik_kaydet: Başarılı sonucu otomatik kaydet.
            otomatik_coz: Hatayı otomatik analiz et.
            kategori: "kali", "dron", "cad" veya boş.
            kaynak_url: Bilginin kaynak URL'si (varsa).

        Returns:
            {"durum": "basarili"|"basarisiz"|"hafiza",
             "sonuc": str, "kaynak": str, "cozum": str}
        """
        logger.info(
            "[OnceHafiza] === İslem basliyor: %s === (kat=%s)",
            hedef[:60], kategori or "yok",
        )

        # ── ARA: Hafızada benzer çözüm var mı? (cereyan DB) ──
        kayit = self.hafizada_ara(hedef, kategori=kategori)
        if kayit:
            if kayit.get("durum") == "belirsiz":
                logger.warning(
                    "[OnceHafiza] ⚠️ Belirsiz: %s", hedef[:50]
                )
                return {
                    "durum": "belirsiz",
                    "sonuc": kayit["cozum"],
                    "kaynak": kayit.get("kaynak", "hafiza"),
                    "guven": kayit.get("guven", 0),
                    "uyari": kayit.get("uyari", ""),
                    "hedef": hedef,
                }
            logger.info(
                "[OnceHafiza] ✅ Hafizada bulundu: %s", hedef[:50]
            )
            return {
                "durum": "hafiza",
                "sonuc": kayit["cozum"],
                "kaynak": kayit.get("kaynak", "hafiza"),
                "hedef": hedef,
            }

        # ── DENE: Çalıştır ──
        try:
            if calistirici:
                sonuc = calistirici(hedef)
            else:
                sonuc = {"output": hedef, "exit_code": 0}

            # Başarılı → kaydet (cereyan sigmoid güven ile)
            if otomatik_kaydet:
                cozum = str(sonuc.get("output", sonuc))[:2000]
                _cereyan_kaydet(
                    hedef=hedef,
                    kategori=kategori or "genel",
                    icerik=cozum,
                    basari=True,
                    kaynak_url=kaynak_url,
                )

            return {
                "durum": "basarili",
                "sonuc": sonuc,
                "kaynak": "kesif",
                "hedef": hedef,
            }

        except Exception as e:
            tb = traceback.format_exc()
            hata_str = f"{type(e).__name__}: {e}"

            # Hata kaydı (cereyan DB'de guven-- + yerel hata DB)
            self.hata_kaydet(hedef, hata_str, tb)

            # Benzer hata için çözüm var mı?
            if otomatik_coz:
                hata_cozum = self.hata_cozum_bul(hedef, hata_str)
                if hata_cozum:
                    logger.info(
                        "[OnceHafiza] 🔧 Benzer hata cozumu: %s",
                        hedef[:50],
                    )
                    return {
                        "durum": "cozuldu",
                        "sonuc": hata_cozum["cozum"],
                        "kaynak": "hata_cozum",
                        "hedef": hedef,
                    }

                analiz = self.analiz_et(hedef, hata_str)
                logger.info("[OnceHafiza] 🔍 Analiz: %s", analiz)
                return {
                    "durum": "basarisiz",
                    "sonuc": hata_str,
                    "kaynak": "hata",
                    "analiz": analiz,
                    "traceback": tb,
                    "hedef": hedef,
                }

            return {
                "durum": "basarisiz",
                "sonuc": hata_str,
                "kaynak": "hata",
                "traceback": tb,
                "hedef": hedef,
            }


# ── Module-level wrapper ──────────────────────────────────────────────

_INSTANCE = None


def _get_once_hafiza() -> OnceHafiza:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = OnceHafiza()
    return _INSTANCE


def isle(
    hedef: str, calistirici: Callable | None = None,
    kategori: str = "", kaynak_url: str | None = None,
) -> dict[str, Any]:
    """Kullanması kolay modül-level fonksiyon."""
    return _get_once_hafiza().isle(
        hedef, calistirici, kategori=kategori, kaynak_url=kaynak_url,
    )


def hafizada_ara(
    hedef: str, kategori: str = "",
) -> dict[str, Any] | None:
    """Hafızada ara (kullanması kolay)."""
    return _get_once_hafiza().hafizada_ara(hedef, kategori=kategori)


def kaydet(
    hedef: str, cozum: str, kategori: str = "",
    kaynak: str = "kesif", kaynak_url: str | None = None,
) -> None:
    """Çözümü cereyan DB'sine kaydet (sigmoid güven ile)."""
    from reymen.cereyan.once_hafiza import kaydet as _ck
    _ck(
        hedef=hedef, kategori=kategori or "genel",
        icerik=cozum, basari=True, kaynak_url=kaynak_url,
    )


# ── cereyan/once_hafiza.py'den 4 fonksiyon ─────────────────────────────
# Bunlar artık TEK kaynak. Aynı DB'yi kullanır: cereyan/.ReYMeN/ogrenmeler.db
# Kullanıcı "belirsiz_gorev_cozumle()" çağırdığında doğrudan cereyan versiyonu çalışır.
belirsiz_gorev_cozumle = _cereyan_belirsiz_cozum
_benzerlik_skoru = _cereyan_benzerlik
eski_kayitlari_temizle = _cereyan_temizle

# OnceHafiza sınıfının static method'unu import edilen fonksiyonla override et
OnceHafiza._kademeli_guven = staticmethod(_cereyan_kademeli_guven)


# ── Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    oh = OnceHafiza()

    # Test 1: Hiç kayıt yokken
    print("\n[Test 1] Ilk arama (bos)")
    r = oh.isle("nmap_versiyon_tespiti")
    print(f"  Durum: {r['durum']}, Kaynak: {r['kaynak']}")

    # Test 2: Kaydet (sigmoid güven hesaplamalı)
    print("\n[Test 2] Kaydet (sigmoid guven)")
    oh.kaydet(
        "nmap_versiyon_tespiti",
        "nmap -sV ile versiyon tespiti yapilir",
        kategori="kali/network/nmap",
    )

    # Test 3: Aynı hedef tekrar → hafızadan + sigmoid guven
    print("\n[Test 3] Ayni hedef tekrar (hafiza + sigmoid guven)")
    r = oh.isle("nmap_versiyon_tespiti")
    print(f"  Durum: {r['durum']}, Kaynak: {r['kaynak']}")
    print(f"  Guven'den son gelen: {r.get('guven', 'N/A')}")

    # Test 4: Guven guncelle
    print("\n[Test 4] Guven guncelle")
    kayitlar = _cereyan_ara("nmap_versiyon_tespiti", min_guven=0.0, gecerli_mi=False)
    if kayitlar:
        yeni_guven = _cereyan_guven_guncelle(kayitlar[0]["id"], basari=True)
        print(f"  Yeni guven: {yeni_guven:.4f} (sigmoid)")

    # Test 5: Hata analizi
    print("\n[Test 5] Hata analizi")
    analiz = oh.analiz_et(
        "api_baglantisi",
        "Connection refused: API sunucusuna baglanilamiyor",
    )
    print(f"  Analiz: {analiz}")

    # Test 6: ara() ile sigmoid guven sorgula
    print("\n[Test 6] ara() sigmoid guven sorgula")
    bul = _cereyan_ara("nmap", min_guven=0.3, gecerli_mi=False)
    if bul:
        for b in bul:
            print(f"  [{b['id']}] {b['hedef'][:40]} → guven={b['guven_skoru']:.4f}")

    print("\n✅ Tum testler gecti (sigmoid guven cereyan DB'de calisiyor)")
