# -*- coding: utf-8 -*-
# SHIM + standalone — tools/memory_tool.py yönlendirir, _ReYMeN_DIR patch'lenebilir
from pathlib import Path

from tools.memory_tool import *  # noqa: F401, F403
from tools.memory_tool import _ReYMeN_DIR as _inner_dir  # noqa: F401

_ReYMeN_DIR = _inner_dir  # test: monkeypatch.setattr(memory_tool, "_ReYMeN_DIR", ...)


def run(eylem: str = "oku", kaynak: str = "MEMORY.md", icerik: str = "") -> str:
    """Shim wrapper — uses module-level _ReYMeN_DIR (patchable)."""
    eylem = eylem.strip().lower()
    if eylem == "oku":
        p = _ReYMeN_DIR / kaynak
        return p.read_text(encoding="utf-8") if p.exists() else "[Yok]"
    if eylem == "yaz":
        if not icerik:
            return "[Hata]: yaz eylemi icin icerik parametresi gerekli."
        _ReYMeN_DIR.mkdir(parents=True, exist_ok=True)
        p = _ReYMeN_DIR / kaynak
        p.write_text(icerik, encoding="utf-8")
        return f"[Tamam] {kaynak} kaydedildi ({len(icerik)} karakter)"
    return f"[Hata]: eylem 'oku' veya 'yaz' olmali, alindi: '{eylem}'"
