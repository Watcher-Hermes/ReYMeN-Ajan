# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands.py — CLI alt komut kayıt merkezi."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


class SubcommandRegistry:
    """Alt komut kayıt merkezi."""

    def __init__(self):
        self._komutlar: Dict[str, dict] = {}

    def kaydet(self, ad: str, func: Callable, aciklama: str = "") -> None:
        self._komutlar[ad] = {"func": func, "aciklama": aciklama}

    def calistir(self, ad: str, *args, **kwargs) -> Any:
        if ad not in self._komutlar:
            raise KeyError(f"Bilinmeyen komut: {ad}")
        return self._komutlar[ad]["func"](*args, **kwargs)

    def listele(self) -> List[str]:
        return sorted(self._komutlar.keys())


_kayit = SubcommandRegistry()


def kaydet(ad: str, func: Callable, aciklama: str = "") -> None:
    _kayit.kaydet(ad, func, aciklama)


def calistir(ad: str, *args, **kwargs) -> Any:
    return _kayit.calistir(ad, *args, **kwargs)


def listele() -> List[str]:
    return _kayit.listele()


if __name__ == "__main__":
    print("subcommands importlandı. Komutlar:", listele())
