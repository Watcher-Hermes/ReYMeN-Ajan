# -*- coding: utf-8 -*-
"""Kalan Hermes skill'lerini Skiller/ altina tasi + eski koku temizle."""

import os
import shutil
from pathlib import Path

PROJE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
KAYNAK = PROJE / "skills"
HEDEF = PROJE / "reymen" / "cereyan" / "skills" / "Skiller"

# Kategori mapping
KAT_MAP = {
    "software-development": "Kod", "devops": "DevOps",
    "mlops": "AI_ML", "data-science": "AI_ML", "ecc": "AI_ML",
    "security": "Guvenlik", "kali-pentest": "Guvenlik",
    "windows-automation": "Windows", "windows-shortcuts": "Windows",
    "creative": "Yaratici", "media": "Yaratici", "gaming": "Yaratici",
    "video": "Yaratici", "content-creation": "Yaratici",
    "productivity": "Verimlilik", "note-taking": "Verimlilik",
    "email": "Verimlilik", "communication": "Verimlilik",
    "user-preferences": "Verimlilik",
    "research": "Research", "github": "Github",
    "android": "android", "smart-home": "android", "mobile": "android",
    "apple": "apple", "web": "Kod", "mcp": "Kod", "workflow": "Kod",
    "reymen": "reymen", "hermes-agent": "reymen", "sistem": "Sistem",
    "autonomous-ai-agents": "AI_ML",
    "self-improvement": "AI_ML", "test-category": "Test", "test-eval": "Test",
}

tasinan = 0
atlanan = 0

for hermes_kat in sorted(os.listdir(KAYNAK)):
    kat_yolu = KAYNAK / hermes_kat
    if not kat_yolu.is_dir():
        continue
    for skill_adi in sorted(os.listdir(kat_yolu)):
        skill_dosya = kat_yolu / skill_adi / "SKILL.md"
        if not skill_dosya.exists():
            continue

        rk = KAT_MAP.get(hermes_kat, "Kod")  # fallback
        hedef_dosya = HEDEF / rk / f"{skill_adi}.md"

        if hedef_dosya.exists():
            atlanan += 1
            continue

        os.makedirs(hedef_dosya.parent, exist_ok=True)
        shutil.copy2(skill_dosya, hedef_dosya)
        tasinan += 1

print(f"Tasinan: {tasinan}")
print(f"Atlanan (zaten var): {atlanan}")
print(f"Kalan: {len(os.listdir(KAYNAK))} kategori")

# Eski koku temizle (INDEX.md haric)
for item in KAYNAK.iterdir():
    if item.name == "INDEX.md":
        continue
    if item.is_dir():
        shutil.rmtree(item)
        print(f"  Silindi: {item.name}/")
    elif item.is_file():
        item.unlink()
        print(f"  Silindi: {item.name}")

print(f"\nproje/skills/ temizlendi (INDEX.md haric)")
