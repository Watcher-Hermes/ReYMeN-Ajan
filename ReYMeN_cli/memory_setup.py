# -*- coding: utf-8 -*-
"""ReYMeN_cli/memory_setup.py — Hafiza Kurulum CLI.

ReYMeN icin hafiza saglayici (memory provider) yapilandirmasi.
ChromaDB, vektorel_hafiza ve diger bellek bilesenlerinin
durumunu kontrol eder, kurulum yapar ve sifirlar.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional


class Renk:
    """ReYMeN Renk sinifi — memory_setup ciktisi icin."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    MOR = "\033[95m"
    KALIN = "\033[1m"
    SOLUK = "\033[2m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)

    @classmethod
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


PROJE_KOK = Path(__file__).parent.parent
CHROMA_KLASOR = PROJE_KOK / ".ReYMeN" / "chroma"
MEM_KLASOR = PROJE_KOK / ".ReYMeN" / "memories"
HAFIZA_CONFIG = PROJE_KOK / ".ReYMeN" / "memory_config.json"


def _chroma_kontrol() -> dict:
    """ChromaDB'nin kullanilabilirlik durumunu kontrol et."""
    try:
        import chromadb  # noqa: F401
        chroma_var = True
    except ImportError:
        chroma_var = False

    durum = {
        "yuklu": chroma_var,
        "klasor_var": CHROMA_KLASOR.exists(),
        "koleksiyon_sayisi": 0,
        "toplam_kayit": 0,
    }

    if chroma_var and CHROMA_KLASOR.exists():
        try:
            from chromadb.config import Settings
            client = chromadb.Client(Settings(
                persist_directory=str(CHROMA_KLASOR),
                anonymized_telemetry=False,
            ))
            koleksiyonlar = client.list_collections()
            durum["koleksiyon_sayisi"] = len(koleksiyonlar)
            for col in koleksiyonlar:
                durum["toplam_kayit"] += col.count()
        except Exception:
            pass

    return durum


def _vektorel_hafiza_kontrol() -> dict:
    """Vektorel hafiza durumunu kontrol et."""
    try:
        sys.path.insert(0, str(PROJE_KOK))
        from vektorel_hafiza import vektorel_hafiza_sistemini_kur, anlamsal_hafiza_ara

        collection = vektorel_hafiza_sistemini_kur(str(CHROMA_KLASOR))
        durum = {
            "hazir": collection is not None,
            "tip": "chromadb" if hasattr(collection, "count") else "basit_yedek",
        }

        if collection is not None and durum["tip"] == "chromadb":
            try:
                durum["kayit_sayisi"] = collection.count()
            except Exception:
                durum["kayit_sayisi"] = 0
        else:
            durum["kayit_sayisi"] = 0

        return durum
    except Exception as e:
        return {"hazir": False, "tip": "hata", "hata": str(e)}


def memory_durum() -> str:
    """Mevcut hafiza saglayici durumunu kontrol et.

    Returns:
        str: Renkli durum raporu.
    """
    try:
        chroma = _chroma_kontrol()
        vektor = _vektorel_hafiza_kontrol()

        satirlar = [
            f"{Renk.kalin('[Memory] Hafiza Sistemi Durumu')}",
            f"{Renk.cyan('ChromaDB Durumu:')}",
        ]

        # ChromaDB
        if chroma["yuklu"]:
            satirlar.append(f"  {Renk.yesil('✓')} Kutuphane: Yuklu")
        else:
            satirlar.append(f"  {Renk.kirmizi('✗')} Kutuphane: Kurulu degil")

        if chroma["klasor_var"]:
            boyut = sum(
                f.stat().st_size for f in CHROMA_KLASOR.rglob("*") if f.is_file()
            )
            satirlar.append(
                f"  {Renk.yesil('✓')} Klasor: {CHROMA_KLASOR} "
                f"({boyut / 1024:.1f} KB)"
            )
        else:
            satirlar.append(f"  {Renk.sari('○')} Klasor: Henuz olusturulmamis")

        satirlar.append(
            f"  Koleksiyon: {chroma['koleksiyon_sayisi']} | "
            f"Toplam kayit: {chroma['toplam_kayit']}"
        )

        # Vektorel hafiza
        satirlar.append(f"{Renk.cyan('Vektorel Hafiza:')}")
        if vektor.get("hazir"):
            satirlar.append(
                f"  {Renk.yesil('✓')} Durum: Hazir ({vektor['tip']})"
            )
            satirlar.append(f"  Kayit: {vektor.get('kayit_sayisi', 0)}")
        else:
            hata = vektor.get("hata", "Bilinmeyen")
            satirlar.append(f"  {Renk.kirmizi('✗')} Durum: Hata - {hata}")

        # Bellek dosyalari
        satirlar.append(f"{Renk.cyan('Bellek Dosyalari:')}")
        if MEM_KLASOR.exists():
            dosyalar = [f for f in MEM_KLASOR.iterdir() if f.is_file()]
            satirlar.append(f"  Dosya sayisi: {len(dosyalar)}")
            for d in dosyalar:
                satirlar.append(f"    + {d.name} ({d.stat().st_size} B)")
        else:
            satirlar.append(f"  {Renk.sari('○')} Bellek klasoru yok")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Memory]')} Durum kontrol hatasi: {e}"


def memory_kurulum(provider: str = "chroma") -> str:
    """Hafiza saglayicisini kur.

    Args:
        provider: Saglayici adi (chroma/vector/basic).

    Returns:
        str: Kurulum sonucu.
    """
    try:
        if provider == "chroma":
            satirlar = [
                f"{Renk.kalin('[Memory] ChromaDB Kurulumu')}",
            ]

            # ChromaDB'yi dene
            try:
                import chromadb  # noqa: F401
                satirlar.append(f"  {Renk.yesil('✓')} ChromaDB zaten yuklu.")
            except ImportError:
                satirlar.append(
                    f"  {Renk.sari('○')} ChromaDB kurulu degil. "
                    f"Kurmak icin: pip install chromadb"
                )

            # Klasoru olustur
            CHROMA_KLASOR.mkdir(parents=True, exist_ok=True)
            satirlar.append(
                f"  {Renk.yesil('✓')} Klasor olusturuldu: {CHROMA_KLASOR}"
            )

            # Config dosyasini yaz
            config = {
                "provider": "chroma",
                "persist_dir": str(CHROMA_KLASOR),
                "collection": "ReYMeN_memory",
                "kurulum_zamani": __import__("datetime").datetime.now().isoformat(),
            }
            HAFIZA_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            with open(str(HAFIZA_CONFIG), "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            satirlar.append(
                f"  {Renk.yesil('✓')} Config kaydedildi: {HAFIZA_CONFIG}"
            )

            # ChromaDB'yi baslatmayi dene
            try:
                import chromadb
                from chromadb.config import Settings

                client = chromadb.Client(Settings(
                    persist_directory=str(CHROMA_KLASOR),
                    anonymized_telemetry=False,
                ))
                client.get_or_create_collection(
                    name="ReYMeN_memory",
                    metadata={"hnsw:space": "cosine"},
                )
                satirlar.append(
                    f"  {Renk.yesil('✓')} Koleksiyon 'ReYMeN_memory' hazir."
                )
            except Exception as e:
                satirlar.append(
                    f"  {Renk.sari('○')} Koleksiyon olusturulamadi: {e}"
                )

            satirlar.append(
                f"\n{Renk.yesil('[Memory] Kurulum tamamlandi.')}"
            )
            return "\n".join(satirlar)

        elif provider == "vector":
            # Vektorel hafiza kurulumu
            satirlar = [
                f"{Renk.kalin('[Memory] Vektorel Hafiza Kurulumu')}",
            ]
            CHROMA_KLASOR.mkdir(parents=True, exist_ok=True)
            MEM_KLASOR.mkdir(parents=True, exist_ok=True)

            try:
                sys.path.insert(0, str(PROJE_KOK))
                from vektorel_hafiza import vektorel_hafiza_sistemini_kur

                col = vektorel_hafiza_sistemini_kur(str(CHROMA_KLASOR))
                if col is not None:
                    satirlar.append(f"  {Renk.yesil('✓')} Vektorel hafiza hazir.")
                else:
                    satirlar.append(f"  {Renk.kirmizi('✗')} Vektorel hafiza baslatilamadi.")
            except Exception as e:
                satirlar.append(f"  {Renk.kirmizi('✗')} Hata: {e}")

            return "\n".join(satirlar)

        elif provider == "basic":
            # Basit bellek dosyasi kurulumu
            MEM_KLASOR.mkdir(parents=True, exist_ok=True)
            for dosya_adi in ["MEMORY.md", "USER.md"]:
                dosya = MEM_KLASOR / dosya_adi
                if not dosya.exists():
                    with open(str(dosya), "w", encoding="utf-8") as f:
                        f.write(f"# {dosya_adi}\n\n_ReYMeN bellek dosyasi._\n")
            return (
                f"{Renk.yesil('[Memory]')} Basit bellek kurulumu tamamlandi.\n"
                f"  Klasor: {MEM_KLASOR}"
            )

        else:
            return f"{Renk.kirmizi('[Memory]')} Bilinmeyen saglayici: {provider}"

    except Exception as e:
        return f"{Renk.kirmizi('[Memory]')} Kurulum hatasi: {e}"


def memory_sifirla(provider: Optional[str] = None) -> str:
    """Hafiza saglayicisini sifirla.

    Args:
        provider: Sifirlanacak saglayici (None=tumu).

    Returns:
        str: Sifirlama sonucu.
    """
    try:
        satirlar = [
            f"{Renk.kalin('[Memory] Hafiza Sifirlama')}",
        ]

        if provider is None or provider == "chroma":
            if CHROMA_KLASOR.exists():
                shutil.rmtree(str(CHROMA_KLASOR))
                satirlar.append(f"  {Renk.yesil('✓')} ChromaDB klasoru silindi.")
            CHROMA_KLASOR.mkdir(parents=True)
            satirlar.append(f"  {Renk.yesil('✓')} ChromaDB klasoru yeniden olusturuldu.")

        if provider is None or provider == "memory":
            if MEM_KLASOR.exists():
                shutil.rmtree(str(MEM_KLASOR))
                satirlar.append(f"  {Renk.yesil('✓')} Bellek klasoru silindi.")
            MEM_KLASOR.mkdir(parents=True)
            for dosya_adi in ["MEMORY.md", "USER.md"]:
                dosya = MEM_KLASOR / dosya_adi
                with open(str(dosya), "w", encoding="utf-8") as f:
                    f.write(f"# {dosya_adi}\n\n_Hafiza sifirlandi._\n")
                satirlar.append(f"  {Renk.yesil('✓')} {dosya_adi} yeniden olusturuldu.")

        if provider is None or provider == "config":
            if HAFIZA_CONFIG.exists():
                HAFIZA_CONFIG.unlink()
                satirlar.append(f"  {Renk.yesil('✓')} Config dosyasi silindi.")

        satirlar.append(f"\n{Renk.yesil('[Memory] Sifirlama tamamlandi.')}")
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Memory]')} Sifirlama hatasi: {e}"


def memory_bilgi() -> str:
    """Hafiza kullanim istatistiklerini goster.

    Returns:
        str: Renkli istatistik raporu.
    """
    try:
        chroma = _chroma_kontrol()
        vektor = _vektorel_hafiza_kontrol()

        toplam_boyut = 0
        dosya_sayisi = 0
        if MEM_KLASOR.exists():
            for f in MEM_KLASOR.rglob("*"):
                if f.is_file():
                    toplam_boyut += f.stat().st_size
                    dosya_sayisi += 1

        chroma_boyut = 0
        if CHROMA_KLASOR.exists():
            for f in CHROMA_KLASOR.rglob("*"):
                if f.is_file():
                    chroma_boyut += f.stat().st_size

        satirlar = [
            f"{Renk.kalin('[Memory] Hafiza Kullanim Istatistikleri')}",
            f"",
            f"{Renk.cyan('ChromaDB:')}",
            f"  Koleksiyon: {chroma['koleksiyon_sayisi']}",
            f"  Kayit: {chroma['toplam_kayit']}",
            f"  Disk: {chroma_boyut / 1024:.1f} KB",
            f"",
            f"{Renk.cyan('Vektorel Hafiza:')}",
            f"  Durum: {'Hazir' if vektor.get('hazir') else 'Kapali'}",
            f"  Tip: {vektor.get('tip', 'bilinmiyor')}",
            f"  Kayit: {vektor.get('kayit_sayisi', 0)}",
            f"",
            f"{Renk.cyan('Bellek Dosyalari:')}",
            f"  Dosya: {dosya_sayisi}",
            f"  Disk: {toplam_boyut / 1024:.1f} KB",
            f"",
            f"{Renk.kalin('Toplam:')} {chroma['toplam_kayit'] + vektor.get('kayit_sayisi', 0)} kayit, "
            f"{(chroma_boyut + toplam_boyut) / 1024:.1f} KB",
        ]

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Memory]')} Bilgi hatasi: {e}"
