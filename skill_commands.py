# -*- coding: utf-8 -*-
"""SHIM — agent/skill_commands.py yönlendirir"""
from agent.skill_commands import *  # noqa: F401, F403


def listele(kategori: str = "", ayrintili: bool = False) -> str:
    """Skill'leri listele."""
    from reymen.arac.skill_utils import SKILLS_KLASORLERI
    sonuclar = []
    for klasor in SKILLS_KLASORLERI:
        if klasor.exists():
            dosyalar = list(klasor.rglob("SKILL.md"))
            if kategori:
                dosyalar = [d for d in dosyalar if kategori in d.parent.name or kategori in d.parent.parent.name]
            sonuclar.extend(dosyalar)
    if not sonuclar:
        return "[Skill] Skill bulunamadi."
    satirlar = [f"[Skill] Toplam {len(sonuclar)} skill:"]
    for d in sorted(sonuclar)[:100]:
        from reymen.arac.skill_utils import SKILLS_KLASORLERI
        try:
            rel = d.relative_to(SKILLS_KLASORLERI[0])
        except ValueError:
            try:
                rel = d.relative_to(SKILLS_KLASORLERI[1])
            except ValueError:
                rel = d
        satirlar.append(f"  - {rel}")
    return "\n".join(satirlar)


def istatistik() -> str:
    """Skill istatistiklerini goster."""
    from reymen.arac.skill_utils import SKILLS_KLASORLERI
    toplam = 0
    for klasor in SKILLS_KLASORLERI:
        if klasor.exists():
            toplam += len(list(klasor.rglob("SKILL.md")))
    return f"Toplam SKILL.md dosyasi: {toplam}"
