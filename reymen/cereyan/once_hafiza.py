# -*- coding: utf-8 -*-
"""
once_hafiza.py — Hafıza-öncelikli çalışma motoru.

Her görev önce hafızaya bakar, bilgi varsa direkt uygular,
yoksa dener, sonucu kaydeder.

Kullanım:
    sonuc = once_hafiza.isle(
        hedef="nmap ile port tara",
        kategori="kali/network",
        calistir=lambda: kali_sandbox.calistir("nmap --help")
    )
"""

from __future__ import annotations

# ── __all__ (cereyan = TEK kaynak, sistem import * ile alır) ──────────────
__all__ = [
    # Module-level fonksiyonlar (cereyan'ın çekirdeği)
    "kaydet", "ara", "hafizada_ara", "guven_guncelle",
    "eski_kayitlari_temizle", "isle", "istatistik",
    "belirsiz_gorev_cozumle",
    # Private yardımcılar (sistem/main.py kullanır)
    "_kademeli_guven", "_benzerlik_skoru", "_get_once_hafiza",
    # Class
    "OnceHafiza",
]

import json
import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ── Varsayılan yol ────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
DB_YOLU = ROOT / ".ReYMeN" / "ogrenmeler.db"

# 6 ay = ~180 gün
GECERLILIK_GUN = 180

_yazma_kilit = threading.Lock()


# ── Kademeli Güven Fonksiyonu ─────────────────────────────────────────────

def _kademeli_guven(basari: int, hata: int) -> float:
    """
    Sigmoid benzeri kademeli güven hesaplama.

    İlk başarıda 0.5, 3 başarıda ~0.75, 10 başarıda ~0.95.
    Hata oranı arttıkça güven düşer.

    Formül: 1 / (1 + e^(-0.5 * (basari - hata - 1)))
    - İlk kayıt (1 basari, 0 hata): 0.5
    - 3 basari, 0 hata: ~0.73
    - 10 basari, 0 hata: ~0.99
    - 1 basari, 3 hata: ~0.12
    """
    import math
    net = basari - hata - 1  # -1 offset: ilk kayıtta 0.5
    return 1.0 / (1.0 + math.exp(-0.5 * net))


# ── Veritabanı ────────────────────────────────────────────────────────────

def _kur(con: sqlite3.Connection) -> None:
    """ogrenmeler tablosunu oluştur."""
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
        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_gecerli ON ogrenmeler(gecerlilik_tarihi);
    """)

    # Migration: eski tablolara kaynak_url ekle (güvenli, sadece yoksa)
    try:
        con.execute("ALTER TABLE ogrenmeler ADD COLUMN kaynak_url TEXT DEFAULT NULL")
    except Exception:
        pass  # Kolon zaten varsa hata verme


@contextmanager
def _baglanti():
    con = sqlite3.connect(str(DB_YOLU), timeout=15, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _db_kur():
    DB_YOLU.parent.mkdir(parents=True, exist_ok=True)
    with _baglanti() as con:
        _kur(con)


# ── Ana API ───────────────────────────────────────────────────────────────

def kaydet(
    hedef: str,
    kategori: str = "genel",
    icerik: str = "",
    basari: bool = True,
    gecerlilik_gun: int = GECERLILIK_GUN,
    kaynak_url: str | None = None,
) -> int:
    """
    Yeni öğrenme kaydı oluştur veya varsa güncelle.

    Args:
        hedef: Görev tanımı (örn. "nmap ile port tara")
        kategori: "kali", "dron", "cad", "kali/network" vb.
        icerik: Öğrenilen bilgi / çözüm
        basari: Başarılı mı?
        gecerlilik_gun: Kaç gün geçerli? (default: 180)
        kaynak_url: Bilginin kaynağı (web URL'si) (default: None)

    Returns:
        Kayıt ID'si
    """
    _db_kur()
    bugun = date.today().isoformat()
    gecerlilik = (date.today() + timedelta(days=gecerlilik_gun)).isoformat()

    with _yazma_kilit:
        with _baglanti() as con:
            # Daha önce aynı hedef+kategori var mı?
            var = con.execute(
                "SELECT id, basari_sayisi, hata_sayisi, guven_skoru FROM ogrenmeler "
                "WHERE hedef = ? AND kategori = ? LIMIT 1",
                (hedef, kategori),
            ).fetchone()

            if var:
                kayit_id, basari_once, hata_once, guven_once = var
                yeni_basari = basari_once + (1 if basari else 0)
                yeni_hata = hata_once + (0 if basari else 1)
                toplam = yeni_basari + yeni_hata
                # Kademeli güven: sigmoid benzeri, 3 başarıda ~0.75
                guven = round(_kademeli_guven(yeni_basari, yeni_hata), 4)

                con.execute(
                    """UPDATE ogrenmeler SET
                        icerik = ?,
                        guven_skoru = ?,
                        basari_sayisi = ?,
                        hata_sayisi = ?,
                        son_kullanim = ?,
                        gecerlilik_tarihi = ?,
                        kaynak_url = COALESCE(?, kaynak_url),
                        guncelleme = datetime('now')
                    WHERE id = ?""",
                    (icerik, guven, yeni_basari, yeni_hata,
                     bugun, gecerlilik, kaynak_url, kayit_id),
                )
                logger.info("[Hafiza] Guncellendi: %s/%s (guven=%.2f, %d basari, %d hata)",
                           kategori, hedef[:40], guven, yeni_basari, yeni_hata)
                return kayit_id
            else:
                # İlk kayıt: guven=0.5 başlangıç, kademeli artar
                baslangic_guven = 0.5 if basari else 0.1
                con.execute(
                    """INSERT INTO ogrenmeler
                       (hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi,
                        son_kullanim, gecerlilik_tarihi, kaynak_url)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (hedef, kategori, icerik,
                     baslangic_guven,
                     1 if basari else 0,
                     0 if basari else 1,
                     bugun, gecerlilik, kaynak_url),
                )
                kayit_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                logger.info("[Hafiza] Yeni kayit: %s/%s (id=%d, guven=%.2f)",
                           kategori, hedef[:40], kayit_id, baslangic_guven)
                return kayit_id


def ara(
    hedef: str,
    kategori: str | None = None,
    min_guven: float = 0.3,
    gecerli_mi: bool = True,
) -> list[dict[str, Any]]:
    """
    Hafızada benzer görev/çözüm ara.

    Her sonuç için `durum` alanı:
      - "guvenilir" → guven_skoru >= 0.5
      - "belirsiz"  → guven_skoru < 0.5

    Args:
        hedef: Aranan görev
        kategori: Sınırla (None = tümü)
        min_guven: Minimum güven skoru (0.0-1.0)
        gecerli_mi: Sadece geçerlilik tarihi geçmemiş olanlar?

    Returns:
        [{"id", "hedef", "kategori", "icerik", "guven_skoru", "durum",
          "son_kullanim", "gecerlilik_tarihi", ...}, ...]
    """
    _db_kur()
    kosullar = ["guven_skoru >= ?"]
    params: list[Any] = [min_guven]

    if kategori:
        kosullar.append("kategori = ?")
        params.append(kategori)

    if gecerli_mi:
        kosullar.append("gecerlilik_tarihi >= date('now')")

    # Tam eşleşme önce, sonra LIKE
    with _baglanti() as con:
        # 1) Tam eşleşme
        tam_sql = (
            "SELECT id, hedef, kategori, icerik, guven_skoru, "
            "basari_sayisi, hata_sayisi, son_kullanim, gecerlilik_tarihi, kaynak_url "
            "FROM ogrenmeler WHERE hedef = ? AND {} "
            "ORDER BY guven_skoru DESC, son_kullanim DESC LIMIT 5"
        ).format(" AND ".join(kosullar))
        tam = con.execute(tam_sql, [hedef] + params).fetchall()

        # 2) Benzer (LIKE)
        benzer_sql = (
            "SELECT id, hedef, kategori, icerik, guven_skoru, "
            "basari_sayisi, hata_sayisi, son_kullanim, gecerlilik_tarihi, kaynak_url "
            "FROM ogrenmeler WHERE hedef LIKE ? AND {} "
            "ORDER BY guven_skoru DESC, son_kullanim DESC LIMIT 5"
        ).format(" AND ".join(kosullar))
        benzer = con.execute(benzer_sql, ["%{}%".format(hedef)] + params).fetchall()

    # Birleştir, duplicate'leri at
    gorulen: set[int] = set()
    sonuc = []
    for row in tam + benzer:
        if row[0] not in gorulen:
            gorulen.add(row[0])
            guven = row[4]
            sonuc.append({
                "id": row[0],
                "hedef": row[1],
                "kategori": row[2],
                "icerik": row[3],
                "guven_skoru": guven,
                "durum": "guvenilir" if guven >= 0.5 else "belirsiz",
                "basari_sayisi": row[5],
                "hata_sayisi": row[6],
                "son_kullanim": row[7],
                "gecerlilik_tarihi": row[8],
                "kaynak_url": row[9] if len(row) > 9 else None,
            })

    return sonuc


def hafizada_ara(
    hedef: str,
    kategori: str | None = None,
    min_guven: float = 0.3,
    gecerli_mi: bool = True,
) -> list[dict[str, Any]]:
    """Alias: ara() ile aynı. Kullanıcı 'hafizada_ara()' dediğinde çalışır."""
    return ara(hedef, kategori, min_guven, gecerli_mi)


def guven_guncelle(kayit_id: int, basari: bool) -> float:
    """
    Bir kaydın güven skorunu güncelle (başarı/hata sayısına göre).

    Returns:
        Yeni güven skoru
    """
    with _yazma_kilit:
        with _baglanti() as con:
            var = con.execute(
                "SELECT basari_sayisi, hata_sayisi FROM ogrenmeler WHERE id = ?",
                (kayit_id,),
            ).fetchone()
            if not var:
                return 0.0

            yeni_basari = var[0] + (1 if basari else 0)
            yeni_hata = var[1] + (0 if basari else 1)
            # Kademeli güven (sigmoid)
            guven = round(_kademeli_guven(yeni_basari, yeni_hata), 4)

            con.execute(
                """UPDATE ogrenmeler SET
                    guven_skoru = ?,
                    basari_sayisi = ?,
                    hata_sayisi = ?,
                    son_kullanim = date('now'),
                    guncelleme = datetime('now')
                WHERE id = ?""",
                (guven, yeni_basari, yeni_hata, kayit_id),
            )

            if basari:
                logger.info("[Hafiza] Basari +1 (id=%d, guven=%.2f)", kayit_id, guven)
            else:
                logger.info("[Hafiza] Hata +1 (id=%d, guven=%.2f)", kayit_id, guven)

            return guven


def eski_kayitlari_temizle(gun_limiti: int = 200) -> int:
    """
    Geçerlilik tarihi geçmiş kayıtları temizle.
    Ama yüksek güvenli (>=0.8) olanları koru.

    Returns:
        Silinen kayıt sayısı
    """
    _db_kur()
    with _yazma_kilit:
        with _baglanti() as con:
            sil = con.execute(
                "DELETE FROM ogrenmeler "
                "WHERE gecerlilik_tarihi < date('now', ?) AND guven_skoru < 0.8",
                ("-{} days".format(gun_limiti),),
            ).rowcount
            if sil:
                logger.info("[Hafiza] %d eski kayit temizlendi.", sil)
            return sil


def isle(
    hedef: str,
    kategori: str = "genel",
    calistir: Callable[[], T] | None = None,
    min_guven: float = 0.5,
    gecerli_mi: bool = True,
    zorla: bool = False,
) -> tuple[T | dict | None, str]:
    """
    *** ANA API — Hafıza-öncelikli görev çalıştırma ***

    Akış:
        1. Hafızada benzer görev ara
        2a. Bulundu + güven >= min_guven + geçerli → önbellekten döndür
        2b. Bulunamadı veya güven düşük → calistir() fonksiyonunu çalıştır
        3. Sonucu hafızaya kaydet
        4. Sonucu döndür

    Args:
        hedef: Görev tanımı
        kategori: Kategori
        calistir: Çalıştırılacak fonksiyon (None = sadece hafıza sorgula)
        min_guven: Önbellek için minimum güven
        gecerli_mi: Geçerlilik kontrolü yap?
        zorla: True = hafızaya bakma, direkt çalıştır

    Returns:
        (sonuc, kaynak)
        sonuc: calistir()'ın döndürdüğü değer veya hafızadaki kayıt
        kaynak: "cache" (hafızadan) / "exec" (çalıştırıldı) / "not_found"
    """
    _db_kur()

    if not zorla:
        kayitlar = ara(hedef, kategori, min_guven=min_guven, gecerli_mi=gecerli_mi)
        if kayitlar:
            en_iyi = kayitlar[0]
            logger.info("[Hafiza] ONBELLEK: %s/%s (guven=%.2f)",
                       en_iyi["kategori"], en_iyi["hedef"][:40], en_iyi["guven_skoru"])
            # Kullanım güncelle
            guven_guncelle(en_iyi["id"], basari=True)

            if calistir is None:
                # Sadece hafıza sorgulama modu
                return en_iyi, "cache"

            # Önbellekte var ama yine de çalıştır? Hayır — direkt döndür
            return en_iyi, "cache"

    if calistir is None:
        return None, "not_found"

    # Çalıştır
    try:
        sonuc = calistir()
        kaydet(hedef, kategori, str(sonuc)[:5000] if sonuc else "", basari=True)
        return sonuc, "exec"
    except Exception as e:
        hata_mesaji = "[HATA] {}: {}".format(type(e).__name__, e)
        logger.warning("[Hafiza] Basarisiz: %s/%s — %s", kategori, hedef[:40], hata_mesaji)
        kaydet(hedef, kategori, hata_mesaji, basari=False)
        raise


def istatistik() -> dict[str, Any]:
    """Hafıza istatistikleri."""
    _db_kur()
    with _baglanti() as con:
        toplam = con.execute("SELECT COUNT(*) FROM ogrenmeler").fetchone()[0]
        gecerli = con.execute(
            "SELECT COUNT(*) FROM ogrenmeler WHERE gecerlilik_tarihi >= date('now')"
        ).fetchone()[0]
        eski = con.execute(
            "SELECT COUNT(*) FROM ogrenmeler WHERE gecerlilik_tarihi < date('now')"
        ).fetchone()[0]
        kategori_say = con.execute(
            "SELECT kategori, COUNT(*) FROM ogrenmeler GROUP BY kategori ORDER BY COUNT(*) DESC"
        ).fetchall()
        ortalama_guven = con.execute(
            "SELECT ROUND(AVG(guven_skoru), 4) FROM ogrenmeler"
        ).fetchone()[0] or 0.0

    return {
        "toplam": toplam,
        "gecerli": gecerli,
        "eski": eski,
        "ortalama_guven": ortalama_guven,
        "kategori_dagilimi": {k: v for k, v in kategori_say},
    }


# ── Belirsiz Görev Çözümleme ──────────────────────────────────────────────

def belirsiz_gorev_cozumle(
    hedef: str,
    esik: float = 0.3,
    max_kategori: int = 3,
) -> dict[str, Any]:
    """
    Belirsiz bir görev geldiğinde hafızadaki en alakalı kategorileri bulur
    ve kullanıcıya tek bir tahmin önerisi hazırlar.

    Akış:
        1. Görevi anahtar kelimelere ayır
        2. Her kategori altındaki kayıtları tara
        3. En alakalı kategoriyi + ilgili kaydı bul
        4. Kullanıcıya soru formatında döndür

    Args:
        hedef: Kullanıcının verdiği belirsiz görev (örn. "sistemi güvenli yap")
        esik: Minimum benzerlik eşiği (0.0-1.0)
        max_kategori: Önerilecek maksimum alternatif kategori sayısı

    Returns:
        {
            "tahmin_kategori": "kali/network" veya None,
            "tahmin_kayit": {...} veya None,
            "guven": 0.75,
            "alternatifler": [...],
            "soru": "Sanırım port taraması yapmak istiyorsun, doğru mu?",
            "ham_hedef": "sistemi güvenli yap"
        }
    """
    _db_kur()

    # 1) Görevi normalize et ve anahtar kelimelere ayır
    kelimeler = _anahtar_kelimeler(hedef)
    if not kelimeler:
        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    with _baglanti() as con:
        # 2) Tüm geçerli kayıtları çek
        tum_kayitlar = con.execute(
            "SELECT id, hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi "
            "FROM ogrenmeler WHERE gecerlilik_tarihi >= date('now') "
            "ORDER BY guven_skoru DESC, basari_sayisi DESC"
        ).fetchall()

    if not tum_kayitlar:
        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    # 3) Her kaydın görevle benzerlik skorunu hesapla
    skorlu: list[tuple[float, dict[str, Any]]] = []
    for row in tum_kayitlar:
        kayit = {
            "id": row[0],
            "hedef": row[1],
            "kategori": row[2],
            "icerik": row[3][:2000],  # 200→2000: referans JSON'un kesilmesini önle
            "guven_skoru": row[4],
            "basari_sayisi": row[5],
            "hata_sayisi": row[6],
        }
        skor = _benzerlik_skoru(hedef, kelimeler, kayit)
        if skor >= esik:
            skorlu.append((skor, kayit))

    # 4) Skora göre sırala
    skorlu.sort(key=lambda x: x[0], reverse=True)

    # 4b) Hiç kelime eşleşmezse en yüksek güvenli kaydı öner (backup)
    if not skorlu:
        # Güven skoru >= 0.8 olan en iyi kaydı bul
        en_guvenli = max(tum_kayitlar, key=lambda r: r[4]) if tum_kayitlar else None
        if en_guvenli and en_guvenli[4] >= 0.8:
            kayit = {
                "id": en_guvenli[0],
                "hedef": en_guvenli[1],
                "kategori": en_guvenli[2],
                "icerik": en_guvenli[3][:2000],  # 200→2000: referans JSON'un kesilmesini önle
                "guven_skoru": en_guvenli[4],
                "basari_sayisi": en_guvenli[5],
                "hata_sayisi": en_guvenli[6],
            }
            kategori = kayit["kategori"]
            kayit_hedef = kayit["hedef"]
            soru = ("Hiçbir kayıt tam eşleşmedi ama en güvenilir bildiğim "
                    + kategori + " kategorisindeki _" + kayit_hedef + "_.\n\n"
                    + "Sanırım **" + kayit_hedef + "** demek istiyorsun, doğru mu?")
            return {
                "tahmin_kategori": kategori,
                "tahmin_kayit": kayit,
                "guven": 0.01,
                "alternatifler": [],
                "soru": soru,
                "ham_hedef": hedef,
            }

        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    # 5) En iyi tahmini seç
    en_iyi_skor, en_iyi_kayit = skorlu[0]

    # Alternatifler (farklı kategorilerden)
    gorulen_kategori: set[str] = set()
    alternatifler = []
    for skor, kayit in skorlu:
        if kayit["kategori"] not in gorulen_kategori and len(alternatifler) < max_kategori:
            gorulen_kategori.add(kayit["kategori"])
            alternatifler.append({"skor": round(skor, 2), **kayit})
            if len(alternatifler) >= max_kategori:
                break

    # 6) Soruyu oluştur
    kategori = en_iyi_kayit["kategori"]
    kayit_hedef = en_iyi_kayit["hedef"]
    satir1 = "Hafızamda **" + kategori + "** kategorisinde _" + kayit_hedef + "_ bilgisi var."
    soru = satir1 + "\n\nSanırım **" + kayit_hedef + "** demek istiyorsun, doğru mu?"

    return {
        "tahmin_kategori": kategori,
        "tahmin_kayit": en_iyi_kayit,
        "guven": round(en_iyi_skor, 2),
        "alternatifler": alternatifler[1:],
        "soru": soru,
        "ham_hedef": hedef,
    }


def _anahtar_kelimeler(metin: str) -> list[str]:
    """Metni temizle ve anlamlı anahtar kelimelere ayır."""
    # Türkçe karakterleri normalize et
    temiz = metin.lower().strip()
    # Noktalama işaretlerini kaldır
    for ch in ".,!?;:()[]{}''\"“”‘’…––/":
        temiz = temiz.replace(ch, " ")
    # Kelimelere ayır
    kelimeler = [k for k in temiz.split() if len(k) > 1]
    return kelimeler


def _benzerlik_skoru(
    hedef: str,
    kelimeler: list[str],
    kayit: dict[str, Any],
) -> float:
    """
    İki metin arasındaki benzerlik skorunu hesapla.

    3 faktör:
    - Anahtar kelime eşleşmesi (hedef kayit.hedef)
    - Kategori eşleşmesi (kelimeler kayit.kategori)
    - Güven skoru bonusu
    """
    kayit_kelimeler = _anahtar_kelimeler(kayit["hedef"] + " " + kayit["kategori"])
    if not kayit_kelimeler:
        return 0.0

    # Kelime eşleşme oranı
    eslesen = sum(1 for k in kelimeler if k in kayit_kelimeler)
    toplam = max(len(kelimeler), len(kayit_kelimeler))
    kelime_skor = eslesen / toplam if toplam > 0 else 0.0

    # Kategori eşleşmesi (kategori adındaki kelimeler)
    kat_kelimeler = _anahtar_kelimeler(kayit["kategori"])
    kat_eslesen = sum(1 for k in kelimeler if k in kat_kelimeler)
    kat_skor = kat_eslesen / max(len(kelimeler), 1) * 0.5  # max 0.5 bonus

    # Güven skoru bonusu (guven > 0.8 ise +0.1, guven > 0.5 ise +0.05)
    guven_bonus = 0.0
    if kayit["guven_skoru"] >= 0.8:
        guven_bonus = 0.1
    elif kayit["guven_skoru"] >= 0.5:
        guven_bonus = 0.05

    # Toplam skor [0.0, 1.0]
    skor = kelime_skor * 0.6 + kat_skor + guven_bonus
    return min(skor, 1.0)


# ── İlk kurulum ───────────────────────────────────────────────────────────
_db_kur()


# ═══════════════════════════════════════════════════════════════════════════════
# OnceHafiza class — Sınıf tabanlı önbellek motoru (eski sistem/once_hafiza)
# ═══════════════════════════════════════════════════════════════════════════════

import os as _os
import sys as _sys
import traceback as _traceback
from datetime import datetime as _datetime, timezone as _timezone


class OnceHafiza:
    """
    Önce Hafızaya Bak prensibi — sınıf tabanlı.

    Her işlem öncesi:
    1. Hafızada benzer çözüm ara
    2. Bulursan direkt uygula (tekrar keşfetme)
    3. Bulamazsan dene + kaydet
    4. Hata olursa analiz et + düzelt + kaydet
    """

    ROOT = ROOT

    @staticmethod
    def _kademeli_guven(basari: int, hata: int) -> float:
        """Sigmoid güven — cereyan/once_hafiza.py fonksiyonuna delege eder."""
        return _kademeli_guven(basari, hata)

    def __init__(
        self,
        skills_db: str | Path = ROOT / ".ReYMeN" / "skills_index.db",
        skills_dir: str | Path = ROOT / "skills",
        ogrenme_db: str | Path = ROOT.parent / "hafiza" / "ogrenme.db",
        hata_db: str | Path = ROOT.parent / "hafiza" / "hatalar.db",
    ):
        self.skills_db = str(skills_db)
        self.skills_dir = str(skills_dir)
        self.ogrenme_db = str(ogrenme_db)
        self.hata_db = str(hata_db)

        _os.makedirs(self.skills_dir, exist_ok=True)
        _os.makedirs(Path(self.ogrenme_db).parent, exist_ok=True)
        _os.makedirs(Path(self.hata_db).parent, exist_ok=True)

        self._db_kur()

    # ── Veritabanı Kurulumu ──────────────────────────────────────────────

    def _db_kur(self) -> None:
        """FTS5 öğrenme + hata veritabanlarını kur."""
        import sqlite3

        # Öğrenme DB
        con = sqlite3.connect(self.ogrenme_db)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript("""
            CREATE TABLE IF NOT EXISTS ogrenmeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hedef TEXT UNIQUE NOT NULL,
                cozum TEXT NOT NULL,
                kaynak TEXT DEFAULT '',
                basari_sayisi INTEGER DEFAULT 1,
                hata_sayisi INTEGER DEFAULT 0,
                son_basari TEXT,
                son_hata TEXT,
                olusturulma TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_hedef ON ogrenmeler(hedef);
        """)
        con.commit()

        # Migration: mevcut DB'ye yeni kolon ekle (fail-safe)
        for col_sql in [
            "ALTER TABLE ogrenmeler ADD COLUMN guven_skoru FLOAT DEFAULT 0.5",
            "ALTER TABLE ogrenmeler ADD COLUMN son_kullanim TEXT",
            "ALTER TABLE ogrenmeler ADD COLUMN kategori TEXT DEFAULT ''",
            "ALTER TABLE ogrenmeler ADD COLUMN gecerlilik_tarihi TEXT",
            "ALTER TABLE ogrenmeler ADD COLUMN kaynak_url TEXT DEFAULT NULL",
        ]:
            try:
                con.execute(col_sql)
            except sqlite3.OperationalError:
                pass  # kolon zaten var
        con.commit()

        # Kolon bazlı index'leri migration sonrası kur
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_kategori ON ogrenmeler(kategori)",
        ]:
            try:
                con.execute(idx_sql)
            except sqlite3.OperationalError:
                pass
        con.commit()
        con.close()

        # Hata DB
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

    # ── ADIM 1: Hafızada Ara ────────────────────────────────────────────

    def hafizada_ara(self, hedef: str, kategori: str = "") -> dict[str, Any] | None:
        """Hafızada benzer çözüm ara."""
        import sqlite3

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
                    logger.info("[OnceHafiza] 🔍 Skills FTS5'te bulundu: %s", row[0])
                    return {"hedef": row[0], "cozum": row[2], "kaynak": row[3] or "skills"}
            except Exception:
                pass
            finally:
                scon.close()
        except Exception:
            pass

        # Öğrenme DB'de ara
        try:
            con = sqlite3.connect(self.ogrenme_db, timeout=5)
            try:
                sql = ("SELECT hedef, cozum, kaynak, basari_sayisi, hata_sayisi, "
                       "gecerlilik_tarihi, guven_skoru, kategori FROM ogrenmeler "
                       "WHERE hedef = ?")
                params = [hedef]
                if kategori:
                    sql += " AND kategori = ?"
                    params.append(kategori)
                sql += " LIMIT 1"
                row = con.execute(sql, params).fetchone()
                if row:
                    guven_skor = row[6] if len(row) > 6 and row[6] is not None else 1.0
                    if guven_skor < 0.5:
                        return {
                            "durum": "belirsiz", "hedef": row[0], "cozum": row[1],
                            "kaynak": row[2] or "ogrenme", "guven": guven_skor,
                            "uyari": f"⚠️ Güven skoru düşük ({guven_skor:.2f})",
                        }
                    gecerli = row[5] if len(row) > 5 else None
                    su_an = _datetime.now(_timezone.utc).strftime("%Y-%m-%d")
                    gecerlilik_asmis = gecerli and gecerli < su_an if gecerli else False

                    if len(row) > 6:
                        basari_say = row[3] if len(row) > 3 else 1
                        hata_say = row[4] if len(row) > 4 else 0
                        yeni_guven = round(self._kademeli_guven(basari_say + 1, hata_say), 4)
                        con.execute(
                            "UPDATE ogrenmeler SET basari_sayisi = basari_sayisi + 1, "
                            "son_basari = datetime('now'), son_kullanim = datetime('now'), "
                            "guven_skoru = ? WHERE hedef = ?",
                            (yeni_guven, hedef),
                        )
                    con.commit()

                    sonuc = {"hedef": row[0], "cozum": row[1], "kaynak": row[2] or "ogrenme", "guven": guven_skor}
                    if len(row) > 7 and row[7]:
                        sonuc["kategori"] = row[7]
                    if gecerlilik_asmis:
                        sonuc["uyari"] = f"⚠️ Geçerlilik tarihi {gecerli} — güncelliğini yitirmiş!"
                    return sonuc
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

        # LIKE araması (kısmi eşleşme)
        try:
            con = sqlite3.connect(self.ogrenme_db, timeout=5)
            try:
                like = f"%{hedef[:50]}%"
                sql = ("SELECT hedef, cozum, kaynak, basari_sayisi, hata_sayisi, "
                       "gecerlilik_tarihi, guven_skoru, kategori FROM ogrenmeler "
                       "WHERE hedef LIKE ?")
                params = [like]
                if kategori:
                    sql += " AND kategori = ?"
                    params.append(kategori)
                sql += " ORDER BY basari_sayisi DESC LIMIT 1"
                row = con.execute(sql, params).fetchone()
                if row:
                    guven_skor = row[6] if len(row) > 6 and row[6] is not None else 1.0
                    if guven_skor < 0.5:
                        return {
                            "durum": "belirsiz", "hedef": row[0], "cozum": row[1],
                            "kaynak": row[2] or "ogrenme_kismi", "guven": guven_skor,
                            "uyari": f"⚠️ Kısmi eşleşme, güven düşük ({guven_skor:.2f})",
                        }
                    return {"hedef": row[0], "cozum": row[1], "kaynak": row[2] or "ogrenme_kismi", "guven": guven_skor}
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

        logger.info("[OnceHafiza] ❌ Hafizada bulunamadi: %s", hedef[:60])
        return None

    # ── ADIM 2: Kaydet ──────────────────────────────────────────────────

    def kaydet(self, hedef: str, cozum: str, kaynak: str = "kesif", kategori: str = "",
               kaynak_url: str | None = None) -> None:
        """Başarılı çözümü öğrenme DB'sine kaydet."""
        import sqlite3

        try:
            con = sqlite3.connect(self.ogrenme_db, timeout=5)
            try:
                su_an = _datetime.now(_timezone.utc)
                bugun = su_an.strftime("%Y-%m-%d")
                gelecek = su_an.replace(
                    month=su_an.month + 6 if su_an.month <= 6 else su_an.month - 6,
                    year=su_an.year + (1 if su_an.month > 6 else 0),
                )
                gecerlilik = gelecek.strftime("%Y-%m-%d")

                mevcut = con.execute(
                    "SELECT basari_sayisi, hata_sayisi FROM ogrenmeler WHERE hedef = ?",
                    (hedef[:500],),
                ).fetchone()
                if mevcut:
                    basari = mevcut[0] + 1
                    hata = mevcut[1]
                    guven = round(self._kademeli_guven(basari, hata), 4)
                else:
                    guven = 0.5

                con.execute(
                    "INSERT INTO ogrenmeler "
                    "(hedef, cozum, kaynak, basari_sayisi, son_basari, son_kullanim, "
                    " guven_skoru, kategori, gecerlilik_tarihi, kaynak_url) "
                    "VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?) "
                    "ON CONFLICT(hedef) DO UPDATE SET "
                    "basari_sayisi = basari_sayisi + 1, "
                    "son_basari = excluded.son_basari, "
                    "son_kullanim = excluded.son_kullanim, "
                    "guven_skoru = ?, "
                    "cozum = excluded.cozum, "
                    "kaynak_url = COALESCE(?, kaynak_url), "
                    "kategori = CASE WHEN excluded.kategori != '' THEN excluded.kategori ELSE kategori END",
                    (hedef[:500], cozum, kaynak, bugun, bugun, guven, kategori[:50], gecerlilik,
                     kaynak_url, guven, kaynak_url),
                )
                con.commit()
                logger.info("[OnceHafiza] ✅ Kaydedildi: %s (guven=%.2f, kategori=%s, gecerlilik=%s)",
                            hedef[:50], guven, kategori or "yok", gecerlilik)
            except Exception as e:
                logger.warning("[OnceHafiza] Kayit hatasi: %s", e)
            finally:
                con.close()
        except Exception as e:
            logger.warning("[OnceHafiza] DB baglanti hatasi: %s", e)

    # ── ADIM 3: Hata Kaydet ─────────────────────────────────────────────

    def hata_kaydet(self, hedef: str, hata: str, tb: str = "") -> None:
        """Hata kaydı tut. Ayrıca ogrenmeler'de hata_sayisi++ ve guven_skoru güncelle."""
        import sqlite3

        try:
            con = sqlite3.connect(self.ogrenme_db, timeout=5)
            try:
                mevcut = con.execute(
                    "SELECT basari_sayisi, hata_sayisi FROM ogrenmeler WHERE hedef = ?",
                    (hedef[:500],),
                ).fetchone()
                if mevcut:
                    basari = mevcut[0]
                    hata_say = mevcut[1] + 1
                    guven = round(self._kademeli_guven(basari, hata_say), 4)
                    con.execute(
                        "UPDATE ogrenmeler SET hata_sayisi = hata_sayisi + 1, "
                        "son_hata = datetime('now'), guven_skoru = ? WHERE hedef = ?",
                        (guven, hedef[:500]),
                    )
                    con.commit()
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

        try:
            con = sqlite3.connect(self.hata_db, timeout=5)
            try:
                con.execute(
                    "INSERT INTO hatalar (hedef, hata, traceback) VALUES (?, ?, ?)",
                    (hedef[:500], str(hata)[:1000], tb[:2000]),
                )
                con.commit()
            except Exception:
                pass
            finally:
                con.close()
        except Exception:
            pass

    def hata_cozum_bul(self, hedef: str, hata: str) -> dict[str, Any] | None:
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

    # ── ADIM 4: Analiz Et (regex+skor bazlı, LLM'siz) ───────────────────

    def analiz_et(self, hedef: str, hata: str) -> str:
        """Hata analizi yap, düzeltme önerisi üret."""
        import re

        hata_lower = (str(hata) or "").lower()

        patterns = {
            "import_hatasi": r"no module named|import error|module.*not found|cannot import",
            "syntax_hatasi": r"invalid syntax|unexpected.*token|eol while|eof while",
            "baglanti_hatasi": r"connection refused|timeout|network.*unreachable|cannot connect",
            "api_hatasi": r"401|403|404|429|500|unauthorized|forbidden|rate limit|api key",
            "dosya_hatasi": r"file not found|no such file|permission denied|is a directory",
            "tip_hatasi": r"attributeerror|typeerror|valueerror|keyerror|indexerror",
            "dll_hatasi": r"dll load|not a valid win32|ordinal not found|entry point",
        }

        eslesen = []
        for kategori, pattern in patterns.items():
            if re.search(pattern, hata_lower):
                eslesen.append(kategori)

        if not eslesen:
            return f"Hata analiz edilemedi, manuel inceleme gerekli:\n{hata[:300]}"

        cozum_onerileri = {
            "import_hatasi": "Eksik paket: `pip install <paket>` veya sys.path kontrol",
            "syntax_hatasi": "Kodda yazım hatası: satır bazlı incele + düzelt",
            "baglanti_hatasi": "Ağ bağlantısı kesik: servis çalışıyor mu kontrol et",
            "api_hatasi": "API anahtarı/sınır sorunu: yetkilendirme veya rate limit",
            "dosya_hatasi": "Dosya yolu hatalı: dizin var mı kontrol et",
            "tip_hatasi": "Değişken tipi uyuşmazlığı: type cast veya None kontrolü",
            "dll_hatasi": "Windows DLL/bağımlılık: yeniden derle veya bağımlılık kur",
        }

        oneriler = [cozum_onerileri.get(k, "Bilinmeyen hata") for k in eslesen]
        return f"Hata sinifi: {', '.join(eslesen)}\nDuzeltme: {' -> '.join(oneriler)}"

    # ── ANA DÖNGÜ ────────────────────────────────────────────────────────

    def isle(
        self,
        hedef: str,
        calistirici: Callable[[str], dict[str, Any]] | None = None,
        otomatik_kaydet: bool = True,
        otomatik_coz: bool = True,
        kategori: str = "",
        kaynak_url: str | None = None,
    ) -> dict[str, Any]:
        """Ana işlem döngüsü: Önce hafızaya bak."""
        logger.info("[OnceHafiza] === İslem basliyor: %s ===", hedef[:60])

        kayit = self.hafizada_ara(hedef, kategori=kategori)
        if kayit:
            if kayit.get("durum") == "belirsiz":
                return {
                    "durum": "belirsiz", "sonuc": kayit["cozum"],
                    "kaynak": kayit.get("kaynak", "hafiza"),
                    "guven": kayit.get("guven", 0), "uyari": kayit.get("uyari", ""),
                    "hedef": hedef,
                }
            return {
                "durum": "hafiza", "sonuc": kayit["cozum"],
                "kaynak": kayit.get("kaynak", "hafiza"), "hedef": hedef,
            }

        try:
            if calistirici:
                sonuc = calistirici(hedef)
            else:
                sonuc = {"output": hedef, "exit_code": 0}

            if otomatik_kaydet:
                cozum = str(sonuc.get("output", sonuc))[:2000]
                self.kaydet(hedef, cozum, kategori=kategori, kaynak_url=kaynak_url)

            return {"durum": "basarili", "sonuc": sonuc, "kaynak": "kesif", "hedef": hedef}

        except Exception as e:
            tb = _traceback.format_exc()
            hata_str = f"{type(e).__name__}: {e}"
            self.hata_kaydet(hedef, hata_str, tb)

            if otomatik_coz:
                hata_cozum = self.hata_cozum_bul(hedef, hata_str)
                if hata_cozum:
                    return {"durum": "cozuldu", "sonuc": hata_cozum["cozum"],
                            "kaynak": "hata_cozum", "hedef": hedef}
                analiz = self.analiz_et(hedef, hata_str)
                return {"durum": "basarisiz", "sonuc": hata_str, "kaynak": "hata",
                        "analiz": analiz, "traceback": tb, "hedef": hedef}

            return {"durum": "basarisiz", "sonuc": hata_str, "kaynak": "hata",
                    "traceback": tb, "hedef": hedef}


# ── Singleton getter ────────────────────────────────────────────────────────

_INSTANCE: OnceHafiza | None = None


def _get_once_hafiza() -> OnceHafiza:
    """Singleton OnceHafiza instance'ı al."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = OnceHafiza()
    return _INSTANCE
