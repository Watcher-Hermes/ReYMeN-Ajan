# -*- coding: utf-8 -*-
"""Tum skill kaynaklarini Skiller/ altinda birlestir + tekrarlari temizle"""

import os, shutil
from pathlib import Path

PROJE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
HEDEF = PROJE / "reymen" / "cereyan" / "skills" / "Skiller"

KAYNAKLAR = [
    ("proje/skills/", PROJE / "skills"),
    ("skills_yeni/", PROJE / "reymen" / "cereyan" / "skills_yeni"),
]

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
    "autonomous-ai-agents": "AI_ML", "self-improvement": "AI_ML",
    "test-category": "Test", "test-eval": "Test",
}

toplam = 0
atlanan = 0
hata = 0

for ad, kaynak in KAYNAKLAR:
    if not kaynak.exists():
        print(f"  {ad}: YOK")
        continue
    
    for hermes_kat in sorted(os.listdir(kaynak)):
        kat_yolu = kaynak / hermes_kat
        if not kat_yolu.is_dir():
            continue
        
        rk = KAT_MAP.get(hermes_kat, "Kod")
        hedef_kat = HEDEF / rk
        os.makedirs(hedef_kat, exist_ok=True)
        
        for skill_adi in sorted(os.listdir(kat_yolu)):
            skill_dosya = kat_yolu / skill_adi / "SKILL.md"
            if not skill_dosya.exists():
                # Belki dogrudan .md dosyasi
                if skill_adi.endswith(".md"):
                    skill_dosya = kat_yolu / skill_adi
                    hedef_dosya = hedef_kat / skill_adi
                else:
                    continue
            else:
                hedef_dosya = hedef_kat / f"{skill_adi}.md"
            
            if hedef_dosya.exists():
                atlanan += 1
                continue
            
            try:
                shutil.copy2(skill_dosya, hedef_dosya)
                toplam += 1
            except Exception as e:
                hata += 1

print(f"Yeni eklenen: {toplam}")
print(f"Atlanan (zaten var): {atlanan}")
print(f"Hata: {hata}")

# Son durum
print("\n=== Skiller/ son durum ===")
for kat in sorted(os.listdir(HEDEF)):
    kat_yolu = HEDEF / kat
    if not kat_yolu.is_dir():
        continue
    md = len(list(kat_yolu.glob("*.md"))) - 1  # INDEX.md haric
    if md > 0:
        print(f"  {kat:20s} | {md:4d} skill")
