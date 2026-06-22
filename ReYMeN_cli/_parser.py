# -*- coding: utf-8 -*-
"""ReYMeN_cli/_parser.py — Ortak Arguman Ayristirici.

Tum CLI modullerinin kullandigi ortak argparse yardimcilarini icerir.
--json, --renk, --sessiz bayraklarini standart hale getirir.
"""

import argparse
import sys
from typing import Any


class _Renk:
    """Basit ANSI renk yardimcisi (Renk sinifi)."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    MAVI = "\033[94m"
    KIRMIZI = "\033[91m"
    CYAN = "\033[96m"
    KALIN = "\033[1m"
    DIM = "\033[2m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, renk_kodu: str) -> str:
        """Metni ANSI renk koduyla boya."""
        return f"{renk_kodu}{metin}{cls.SON}"


def ekle_ortak_argumanlar(parser: argparse.ArgumentParser) -> None:
    """Tum CLI modulleri icin ortak argumanlari parser'a ekle.

    Eklenen argumanlar:
      --json   : JSON formatinda cikti
      --renk   : Renkli cikti (varsayilan: True)
      --sessiz : Sessiz mod (sadece kritik cikti)

    Args:
        parser: Eklemelerin yapilacagi argparse.ArgumentParser nesnesi.
    """
    try:
        parser.add_argument("--json", action="store_true",
                            help=_Renk.boya("JSON cikti ver", _Renk.CYAN))
        parser.add_argument("--renk", action="store_true", default=True,
                            help=_Renk.boya("Renkli cikti acik/kapali", _Renk.YESIL))
        parser.add_argument("--sessiz", action="store_true",
                            help=_Renk.boya("Sessiz mod (minimum cikti)", _Renk.DIM))
    except Exception as e:
        print(f"[Parser] Ortak arguman eklenirken hata: {e}", file=sys.stderr)


def argument_parser(tanim: str, description: str = "") -> argparse.ArgumentParser:
    """Ortak argumanlarla yapilandirilmis bir ArgumentParser olustur.

    Bu fonksiyon tum CLI alt modullerinde kullanilir.
    --json, --renk, --sessiz argumanlari otomatik eklenir.

    Args:
        tanim: Alt komutun kisa tanimi (komut adi olarak kullanilir).
        description: argparse description parametresi (varsayilan: bos).

    Returns:
        argparse.ArgumentParser: Ortak argumanlarla hazir parser.
    """
    try:
        parser = argparse.ArgumentParser(
            prog=tanim,
            description=_Renk.boya(description or f"{tanim} komutu", _Renk.MAVI),
            add_help=True,
        )
        ekle_ortak_argumanlar(parser)
        return parser
    except Exception as e:
        print(f"[Parser] ArgumentParser olusturma hatasi: {e}", file=sys.stderr)
        parser = argparse.ArgumentParser(prog=tanim, description=description)
        ekle_ortak_argumanlar(parser)
        return parser


def parserdan_al(parser: argparse.ArgumentParser, anahtar: str, varsayilan: Any = None) -> Any:
    """Parser namespace'inden guvenli deger oku.

    Anahtar mevcut degilse varsayilan degeri doner.

    Args:
        parser: ArgumentParser nesnesi.
        anahtar: Alinacak attribute adi.
        varsayilan: Anahtar bulunamazsa donulecek deger.

    Returns:
        Attribute degeri veya varsayilan.
    """
    try:
        return getattr(parser, anahtar, varsayilan)
    except Exception:
        return varsayilan
