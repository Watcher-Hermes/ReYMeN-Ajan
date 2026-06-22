# -*- coding: utf-8 -*-
"""ReYMeN_cli/fallback_cmd.py — Yedek Saglayici Zinciri CLI.

Fallback (yedek) saglayici zincirini yonetme komutlari:
listeleme, ekleme, cikarma ve temizleme.
ReYMeN mimarisinde ana saglayici basarisiz oldugunda
kullanilacak yedek saglayicilari tanimlar.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional


class Renk:
    """ReYMeN Renk sinifi — fallback CLI ciktisi icin."""
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
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)


class FallbackCmdError(Exception):
    """Fallback komutlarinda olusan ozel hata."""
    pass


def _fallback_dosyasi(config_path: Optional[str] = None) -> Path:
    """Fallback yapilandirma dosya yolunu bul.

    Args:
        config_path: Ozel config yolu (None ise varsayilan kullanilir).

    Returns:
        Path: Fallback config dosyasi yolu.
    """
    if config_path:
        return Path(config_path)
    # ReYMeN proje kokune gore varsayilan yol
    proje_kok = Path(__file__).parent.parent
    return proje_kok / ".ReYMeN" / "fallback" / "providers.json"


def _fallback_oku(config_path: Optional[str] = None) -> dict:
    """Fallback yapilandirmasini JSON dosyasindan oku.

    Args:
        config_path: Ozel config yolu.

    Returns:
        dict: Fallback yapilandirma. Dosya yoksa bos dict doner.
    """
    try:
        dosya = _fallback_dosyasi(config_path)
        if not dosya.exists():
            return {"zincir": [], "aktif": True}
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"zincir": [], "aktif": True}
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return {"zincir": [], "aktif": True}


def _fallback_yaz(veri: dict, config_path: Optional[str] = None) -> bool:
    """Fallback yapilandirmasini JSON dosyasina yaz.

    Args:
        veri: Kaydedilecek yapilandirma sozlugu.
        config_path: Ozel config yolu.

    Returns:
        bool: Yazma basariliysa True.
    """
    try:
        dosya = _fallback_dosyasi(config_path)
        dosya.parent.mkdir(parents=True, exist_ok=True)
        with open(str(dosya), "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def fallback_list(config: dict) -> str:
    """Mevcut fallback zincirini listele.

    Args:
        config: Fallback yapilandirma sozlugu (genellikle _fallback_oku() ciktisi).

    Returns:
        str: Bicimlendirilmis zincir listesi (renkli).
    """
    try:
        zincir = config.get("zincir", [])
        aktif = config.get("aktif", True)

        if not zincir:
            return (
                f"\n  {Renk.sari('Fallback zinciri bos.')}\n"
                f"  {Renk.sari('Eklemek icin: fallback_add()')}"
            )

        satirlar = [
            f"\n  {Renk.kalin(Renk.cyan('═══ Yedek Saglayici Zinciri ═══'))}",
            f"  {Renk.mor('Durum:')} {Renk.yesil('Aktif') if aktif else Renk.kirmizi('Pasif')}",
            f"  {Renk.mor('Adim:')}  {len(zincir)} yedek saglayici\n",
        ]

        for i, saglayici in enumerate(zincir, 1):
            if isinstance(saglayici, dict):
                ad = saglayici.get("ad", saglayici.get("name", f"Saglayici {i}"))
                model = saglayici.get("model", "varsayilan")
                oncelik = saglayici.get("oncelik", saglayici.get("priority", i))
                satirlar.append(
                    f"    {Renk.cyan(f'{i}.')} {Renk.yesil(ad)} "
                    f"({Renk.mor('model:')} {model}, "
                    f"{Renk.mor('oncelik:')} {oncelik})"
                )
            else:
                satirlar.append(f"    {Renk.cyan(f'{i}.')} {Renk.yesil(str(saglayici))}")

        satirlar.append(Renk.kalin(Renk.cyan('═══════════════════════════\n')))
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Fallback]')} Liste hatasi: {e}"


def fallback_add(config_path: str) -> str:
    """Fallback zincirine yeni bir saglayici ekle (interaktif).

    Kullanicidan saglayici adi, model ve oncelik bilgilerini alir.
    Zincire ekler ve JSON dosyasina kaydeder.

    Args:
        config_path: Fallback config dosya yolu.

    Returns:
        str: Islem sonucu mesaji (renkli).
    """
    try:
        config = _fallback_oku(config_path)
        zincir = config.get("zincir", [])

        print(f"\n  {Renk.cyan('Yeni yedek saglayici bilgileri:')}")
        ad = input(f"  {Renk.mor('Saglayici adi')}: ").strip()
        if not ad:
            return f"  {Renk.sari('Islem iptal edildi (ad bos).')}"

        model = input(f"  {Renk.mor('Model')} [{Renk.sari('varsayilan')}]: ").strip() or "varsayilan"

        oncelik_str = input(f"  {Renk.mor('Oncelik')} [{Renk.sari(str(len(zincir) + 1))}]: ").strip()
        try:
            oncelik = int(oncelik_str) if oncelik_str else len(zincir) + 1
        except ValueError:
            oncelik = len(zincir) + 1

        yeni_saglayici = {
            "ad": ad,
            "model": model,
            "oncelik": oncelik,
        }

        zincir.append(yeni_saglayici)
        config["zincir"] = zincir

        if _fallback_yaz(config, config_path):
            return (
                f"  {Renk.yesil('✓')} Saglayici eklendi: "
                f"{Renk.yesil(ad)} (model: {model}, oncelik: {oncelik})"
            )
        else:
            return f"  {Renk.kirmizi('✗')} Yazma hatasi: config dosyasina yazilamadi."
    except KeyboardInterrupt:
        return f"  {Renk.sari('⚠ Islem iptal edildi.')}"
    except Exception as e:
        return f"  {Renk.kirmizi('✗')} Ekleme hatasi: {e}"


def fallback_remove(config_path: str) -> str:
    """Fallback zincirinden bir saglayici cikar (interaktif).

    Kullanicidan cikarilacak saglayiciyi secer (indeks bazli).
    Zincirden cikarir ve JSON dosyasina kaydeder.

    Args:
        config_path: Fallback config dosya yolu.

    Returns:
        str: Islem sonucu mesaji (renkli).
    """
    try:
        config = _fallback_oku(config_path)
        zincir = config.get("zincir", [])

        if not zincir:
            return f"  {Renk.sari('Fallback zinciri bos, cikarilacak eleman yok.')}"

        print(f"\n  {Renk.cyan('Mevcut zincir:')}")
        for i, sag in enumerate(zincir, 1):
            ad = sag.get("ad", sag.get("name", str(sag))) if isinstance(sag, dict) else str(sag)
            print(f"    {Renk.cyan(f'{i}.')} {Renk.yesil(ad)}")

        secim = input(f"\n  {Renk.mor('Cikarilacak indeks (1-{len(zincir)})')}: ").strip()
        try:
            indeks = int(secim) - 1
            if indeks < 0 or indeks >= len(zincir):
                return f"  {Renk.kirmizi('✗')} Gecersiz indeks: {secim}"
        except ValueError:
            return f"  {Renk.kirmizi('✗')} Gecersiz sayi: {secim}"

        cikarilan = zincir.pop(indeks)
        ad = cikarilan.get("ad", cikarilan.get("name", str(cikarilan))) if isinstance(cikarilan, dict) else str(cikarilan)
        config["zincir"] = zincir

        if _fallback_yaz(config, config_path):
            return f"  {Renk.yesil('✓')} Saglayici cikarildi: {Renk.yesil(ad)}"
        else:
            return f"  {Renk.kirmizi('✗')} Yazma hatasi."
    except KeyboardInterrupt:
        return f"  {Renk.sari('⚠ Islem iptal edildi.')}"
    except Exception as e:
        return f"  {Renk.kirmizi('✗')} Cikarma hatasi: {e}"


def fallback_clear(config_path: str) -> str:
    """Fallback zincirini tamamen temizle.

    Tum saglayicilari zincirden cikarir ve JSON dosyasini gunceller.

    Args:
        config_path: Fallback config dosya yolu.

    Returns:
        str: Islem sonucu mesaji (renkli).
    """
    try:
        config = _fallback_oku(config_path)
        zincir = config.get("zincir", [])
        adet = len(zincir)

        if adet == 0:
            return f"  {Renk.sari('Zincir zaten bos.')}"

        config["zincir"] = []
        if _fallback_yaz(config, config_path):
            return f"  {Renk.yesil('✓')} Zincir temizlendi ({adet} saglayici kaldirildi)."
        else:
            return f"  {Renk.kirmizi('✗')} Yazma hatasi."
    except Exception as e:
        return f"  {Renk.kirmizi('✗')} Temizleme hatasi: {e}"
