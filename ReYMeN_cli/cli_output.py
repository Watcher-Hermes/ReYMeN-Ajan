# -*- coding: utf-8 -*-
"""ReYMeN_cli/cli_output.py — Paylasilan CLI Cikti Yardimcilari.

Tum CLI modullerinin kullandigi renkli cikti ve girdi fonksiyonlari.
ReYMeN ekosisteminde tutarli bir kullanici deneyimi saglar.
"""

import sys


class Renk:
    """ReYMeN Renk sinifi — ANSI renk kodlari ile konsol ciktisi.

    Kullanim:
        Renk.yesil("Basarili!") -> yesil renkli metin
        Renk.hata("Bir sorun var") -> kirmizi renkli metin
    """
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
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


def print_info(text: str) -> None:
    """Bilgi mesaji yazdir."""
    try:
        print(f"  {text}")
    except Exception:
        print(f"  {text}", file=sys.stderr)


def print_success(text: str) -> None:
    """Basarili islem mesaji yazdir (yesil onay isareti ile)."""
    try:
        print(f"{Renk.yesil('✓')} {text}")
    except Exception:
        print(f"✓ {text}")


def print_warning(text: str) -> None:
    """Uyari mesaji yazdir (sari uyari isareti ile)."""
    try:
        print(f"{Renk.sari('⚠')} {text}")
    except Exception:
        print(f"⚠ {text}")


def print_error(text: str) -> None:
    """Hata mesaji yazdir (kirmizi carpı isareti ile)."""
    try:
        print(f"{Renk.kirmizi('✗')} {text}", file=sys.stderr)
    except Exception:
        print(f"✗ {text}", file=sys.stderr)


def print_header(text: str) -> None:
    """Baslik mesaji yazdir (mavi, kalin, ustte bosluklu)."""
    try:
        print(f"\n  {Renk.kalin(Renk.mavi(text))}")
    except Exception:
        print(f"\n  {text}")


def prompt(question: str, default: str | None = None, password: bool = False) -> str:
    """Kullanicidan girdi iste.

    Args:
        question: Kullaniciya sorulacak soru metni.
        default: Varsayilan deger (bos girilirse bu kullanilir).
        password: True ise girilen metin gizlenir (getpass).

    Returns:
        str: Kullanicinin girdigi deger veya varsayilan.
    """
    try:
        suffix = f" [{Renk.sari(str(default))}]" if default else ""
        if password:
            import getpass
            try:
                value = getpass.getpass(f"  {Renk.cyan(question)}{suffix}: ")
            except Exception:
                value = input(f"  {question}{suffix}: ")
        else:
            value = input(f"  {Renk.cyan(question)}{suffix}: ")
        return value.strip() or (default or "")
    except (KeyboardInterrupt, EOFError):
        print()
        return default or ""
    except Exception:
        return default or ""


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Evet/Hayir sorusu sor.

    Args:
        question: Soru metni.
        default: Varsayilan deger (True=evet, False=hayir).

    Returns:
        bool: Kullanicinin cevabi.
    """
    try:
        hint = f"{Renk.yesil('E')}/h" if default else f"e/{Renk.yesil('H')}"
        answer = prompt(f"{question} ({Renk.sari(hint)})")
        if not answer:
            return default
        return answer.lower().startswith("e")
    except Exception:
        return default
