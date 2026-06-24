# -*- coding: utf-8 -*-
# SHIM + standalone — tools/skill_tool.py yönlendirir, SKILLS_DIR patch'lenebilir
from pathlib import Path

from tools.skill_tool import *  # noqa: F401, F403

SKILLS_DIR = Path(__file__).parent / ".ReYMeN" / "skills"


def run(eylem: str = "liste", ad: str = "") -> str:
    """Shim wrapper — uses module-level SKILLS_DIR (patchable)."""
    eylem = eylem.strip().lower()

    if eylem == "liste":
        if not SKILLS_DIR.exists():
            return "[Bilgi] Skill bulunamadi."
        skills = sorted(SKILLS_DIR.rglob("*.md"))
        if not skills:
            return "[Bilgi] Skill bulunamadi."
        satirlar = [f"Skill ({len(skills)}):"]
        for s in skills[:50]:
            rel = s.relative_to(SKILLS_DIR)
            satirlar.append(f"  - {rel}")
        return "\n".join(satirlar)

    if eylem == "goruntule":
        if not ad:
            return "[Hata]: ad parametresi gerekli."
        hedef = SKILLS_DIR / f"{ad}.md"
        if not hedef.exists():
            eslesme = next(SKILLS_DIR.rglob(f"{ad}.md"), None) if SKILLS_DIR.exists() else None
            if eslesme is None:
                return f"[Hata]: '{ad}' skill bulunamadi."
            hedef = eslesme
        return hedef.read_text(encoding="utf-8")

    return f"[Hata]: eylem 'liste' veya 'goruntule' olmali, alindi: '{eylem}'"
