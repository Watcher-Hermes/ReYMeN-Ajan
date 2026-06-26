# -*- coding: utf-8 -*-
"""
skill_sync_all.py — Hermes skills -> ReYMeN cereyan/skills/Skiller/ toplu kopyalama

1) proje/skills/<kategori>/<skill>/SKILL.md -> Skiller/<Rkategori>/<skill>.md
2) Hermes hub'dan eksik skill'leri skill_view ile oku -> Skiller/ altına yaz
3) İkilik yok, tek depo: reymen/cereyan/skills/Skiller/
"""

import json
import os
import shutil
import sys
from pathlib import Path

# ── Yollar ──────────────────────────────────────────────────────────────────
PROJE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
KAYNAK_SKILLS = PROJE / "skills"  # Hermes formatli
HEDEF_SKILLER = PROJE / "reymen" / "cereyan" / "skills" / "Skiller"
ONCEKI_SKILLER = PROJE / "reymen" / "cereyan" / "skills" / "skiller_yeni"
RAPOR_DOSYASI = PROJE / "reymen" / "cereyan" / ".ReYMeN" / "skill_sync_raporu.json"

# ── Kategori Mapping (Hermes -> ReYMeN) ────────────────────────────────────
HERMES_TO_REYMEN = {
    "software-development": "Kod",
    "devops": "DevOps",
    "autonomous-ai-agents": "AI_ML",
    "mlops": "AI_ML",
    "mlops/evaluation": "AI_ML",
    "mlops/inference": "AI_ML",
    "mlops/models": "AI_ML",
    "mlops/research": "AI_ML",
    "data-science": "AI_ML",
    "security": "Guvenlik",
    "windows-automation": "Windows",
    "windows-shortcuts": "Windows",
    "note-taking": "Kullanici",
    "productivity": "Verimlilik",
    "user-preferences": "Kullanici",
    "communication": "Kullanici",
    "research": "Research",
    "email": "Kullanici",
    "creative": "Yaratici",
    "media": "Medya",
    "gaming": "Gaming",
    "video": "Medya",
    "content-creation": "Medya",
    "smart-home": "smart-home",
    "android": "android",
    "apple": "apple",
    "github": "Github",
    "workflow": "Kod",
    "mcp": "Kod",
    "ecc": "AI_ML",
    "ai/ecc": "AI_ML",
    "reymen": "reymen",
    "test-category": "Test",
    "test-eval": "Test",
    "sistem": "Sistem",
    "kali-pentest": "Guvenlik",
    "voice": "voice",
    "social-media": "sosyal-medya",
    "self-improvement": "AI_ML",
    "web": "Kod",
    "mobile": "android",
    "domain": "Kod",
    "diagramming": "Yaratici",
    "dosya": "Kod",
    "gifs": "Medya",
    "inference-sh": "Kod",
    "index-cache": "Kod",
    "indexing": "Kod",
    "kod": "Kod",
    "lm-baseline": "AI_ML",
    "markdown-viewer": "Kod",
    "minimal-workbench": "Kod",
    "otomasyon": "DevOps",
    "playwright-mcp": "Kod",
    "prompt-*": "AI_ML",
    "sentiment-baseline": "AI_ML",
    "sistem": "Sistem",
    "skill-*": "AI_ML",
    "social-media": "sosyal-medya",
    "text-encoder-picker": "AI_ML",
    "veri": "veri-bilimi",
    "voice": "voice",
    "web": "Kod",
    "windows-automation": "Windows",
    "windows-shortcuts": "Windows",
    "windows-system-automation": "Windows",
    "yuanbao": "sosyal-medya",
}

# Kategorisi bilinmeyenlerin fallback'i
FALLBACK_KATEGORI = "Kod"

# ── İstatistik ──────────────────────────────────────────────────────────────
rapor = {
    "kopyalanan": 0,
    "guncellenen": 0,
    "atlanan": 0,
    "hata": 0,
    "eklenen": 0,
    "detay": [],
}


def kategori_bul(hermes_skill_path: str) -> str:
    """Hermes skill path'inden ReYMeN kategorisi bul."""
    # İlk segment kategori
    parts = hermes_skill_path.replace("\\", "/").split("/")
    
    # Kategorili skill (software-development/acp-auth-fix)
    if len(parts) >= 2:
        kat = parts[0]
        # Alt kategori kontrolü (mlops/inference)
        if len(parts) >= 3 and kat in ("mlops", "ai", "prompt"):
            alt_kat = f"{kat}/{parts[1]}"
            if alt_kat in HERMES_TO_REYMEN:
                return HERMES_TO_REYMEN[alt_kat]
        if kat in HERMES_TO_REYMEN:
            return HERMES_TO_REYMEN[kat]
    
    # Kategorisiz skill (direkt skill adı)
    # İlk kelimeye bak
    ilk_kelime = parts[0].split("-")[0] if parts else ""
    for pattern, rk in HERMES_TO_REYMEN.items():
        if pattern.endswith("*") and parts[0].startswith(pattern[:-1]):
            return rk
    
    return FALLBACK_KATEGORI


def kopyala_hermes_skills():
    """proje/skills/ altındaki tüm Hermes skill'lerini Skiller/ altına kopyala."""
    global rapor
    
    # Kategorileri tara
    for hermes_kat in sorted(os.listdir(KAYNAK_SKILLS)):
        kat_yolu = KAYNAK_SKILLS / hermes_kat
        if not kat_yolu.is_dir():
            continue
        
        # Skill'leri tara
        for skill_adi in sorted(os.listdir(kat_yolu)):
            skill_klasoru = kat_yolu / skill_adi
            skill_dosyasi = skill_klasoru / "SKILL.md"
            if not skill_dosyasi.exists():
                continue
            
            # ReYMeN kategorisini bul
            rkategori = kategori_bul(f"{hermes_kat}/{skill_adi}")
            hedef_klasor = HEDEF_SKILLER / rkategori
            hedef_dosya = hedef_klasor / f"{skill_adi}.md"
            
            # Varsa atla
            if hedef_dosya.exists():
                rapor["atlanan"] += 1
                continue
            
            try:
                os.makedirs(hedef_klasor, exist_ok=True)
                shutil.copy2(skill_dosyasi, hedef_dosya)
                rapor["kopyalanan"] += 1
                rapor["detay"].append({
                    "islem": "kopyala",
                    "kaynak": f"skills/{hermes_kat}/{skill_adi}/SKILL.md",
                    "hedef": f"Skiller/{rkategori}/{skill_adi}.md",
                })
                
                if rapor["kopyalanan"] % 100 == 0:
                    print(f"  {rapor['kopyalanan']} skill kopyalandi...")
                    
            except Exception as e:
                rapor["hata"] += 1
                rapor["detay"].append({
                    "islem": "hata",
                    "kaynak": f"skills/{hermes_kat}/{skill_adi}/SKILL.md",
                    "hata": str(e),
                })


def rapor_kaydet():
    """Raporu JSON olarak kaydet."""
    rapor["toplam_kopyalanan"] = rapor["kopyalanan"]
    rapor["toplam_atlanan"] = rapor["atlanan"]
    rapor["toplam_hata"] = rapor["hata"]
    
    try:
        with open(RAPOR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(rapor, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    
    print(f"\n{'='*50}")
    print(f"RAPOR")
    print(f"{'='*50}")
    print(f"Kopyalanan: {rapor['kopyalanan']}")
    print(f"Atlanan (zaten var): {rapor['atlanan']}")
    print(f"Hata: {rapor['hata']}")
    print(f"Toplam islenen: {rapor['kopyalanan'] + rapor['atlanan'] + rapor['hata']}")
    print(f"Rapor: {RAPOR_DOSYASI}")


if __name__ == "__main__":
    print(f"KAYNAK: {KAYNAK_SKILLS}")
    print(f"HEDEF: {HEDEF_SKILLER}")
    print()
    print("Hermes skill'leri Skiller/ altina kopyalaniyor...")
    print(f"(Sadece olmayanlar eklenecek, var olanlar atlanacak)")
    print()
    
    kopyala_hermes_skills()
    rapor_kaydet()
