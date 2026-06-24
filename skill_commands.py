# -*- coding: utf-8 -*-
"""SHIM — agent/skill_commands.py yönlendirir"""
from agent.skill_commands import *  # noqa: F401, F403

# ReYMeN ek fonksiyonlari — test uyumu
from reymen.arac.skill_utils import (  # noqa: F401
    skill_sayisi as _skill_sayisi,
    _tum_skill_dosyalari as _skill_dosyalari,
)
from pathlib import Path as _Path


def listele() -> list:
    """Tum skill adlarini liste olarak dondur."""
    try:
        return [d.parent.name for d in _skill_dosyalari()]
    except Exception:
        return []


def istatistik() -> str:
    """Skill istatistiklerini metin olarak dondur."""
    try:
        sayac = _skill_sayisi()
        return f"Toplam {sayac} SKILL.md dosyasi bulundu."
    except Exception:
        return "SKILL.md istatistik alinamadi."
