# -*- coding: utf-8 -*-
"""ReYMeN_cli/skill_import.py — Skill import CLI.

GitHub'dan, dosyadan skill import etme ve kaynak listeleme islemleri.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
SKILLS_DIR = PROJE_KOK / ".ReYMeN" / "skills"
SOURCES_FILE = PROJE_KOK / ".ReYMeN" / "skill_sources.json"


def _kaynaklari_oku() -> dict:
    """Kayitli skill kaynaklarini oku."""
    if not SOURCES_FILE.exists():
        return {}
    try:
        with open(str(SOURCES_FILE), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _kaynaklari_yaz(kaynaklar: dict):
    """Skill kaynaklarini kaydet."""
    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(str(SOURCES_FILE), "w", encoding="utf-8") as f:
        json.dump(kaynaklar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Skill import CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: from_github, from_file, list_sources
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["from_github", "from_file", "list_sources"],
                            help="Yapilacak islem (from_github|from_file|list_sources)")
    alt_parser.add_argument("--url", type=str, default=None,
                            help="GitHub repo URL'si veya dosya yolu")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Skill adi")
    alt_parser.add_argument("--branch", type=str, default="main",
                            help="GitHub branch adi")


def calistir(args):
    """Skill import komutunu calistir."""
    try:
        islem = args.islem or "list_sources"
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)

        if islem == "from_github":
            url = args.url
            name = args.name
            branch = args.branch or "main"
            if not url:
                print("[SkillImport] Lutfen --url parametresini belirtin.")
                return
            if not name:
                name = url.rstrip("/").split("/")[-1].replace(".git", "")
            print(f"[SkillImport] GitHub'dan indiriliyor: {url}")
            gecici_klasor = PROJE_KOK / ".temp_skill_clone"
            if gecici_klasor.exists():
                shutil.rmtree(str(gecici_klasor))
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "-b", branch, url, str(gecici_klasor)],
                    check=True, capture_output=True, text=True
                )
            except subprocess.CalledProcessError as e:
                print(f"[SkillImport] Git clone hatasi: {e.stderr}")
                if gecici_klasor.exists():
                    shutil.rmtree(str(gecici_klasor))
                return
            md_dosyalari = list(gecici_klasor.rglob("*.md"))
            if not md_dosyalari:
                print("[SkillImport] Repo'da .md skill dosyasi bulunamadi.")
                shutil.rmtree(str(gecici_klasor))
                return
            import_edilen = 0
            for md_dosya in md_dosyalari:
                hedef = SKILLS_DIR / md_dosya.name
                shutil.copy2(str(md_dosya), str(hedef))
                import_edilen += 1
                print(f"  + Import edildi: {md_dosya.name}")
            shutil.rmtree(str(gecici_klasor))
            kaynaklar = _kaynaklari_oku()
            kaynaklar[name] = {
                "url": url,
                "branch": branch,
                "tarih": datetime.now().isoformat(),
                "dosya_sayisi": import_edilen,
            }
            _kaynaklari_yaz(kaynaklar)
            print(f"[SkillImport] {import_edilen} skill import edildi (kaynak: {name})")

        elif islem == "from_file":
            url = args.url
            name = args.name
            if not url:
                print("[SkillImport] Lutfen --url (dosya yolu) parametresini belirtin.")
                return
            kaynak = Path(url)
            if not kaynak.exists():
                alternatif = PROJE_KOK / url
                if alternatif.exists():
                    kaynak = alternatif
                else:
                    print(f"[SkillImport] Dosya bulunamadi: {url}")
                    return
            if not name:
                name = kaynak.stem
            hedef = SKILLS_DIR / kaynak.name
            shutil.copy2(str(kaynak), str(hedef))
            kaynaklar = _kaynaklari_oku()
            if "yerel_dosyalar" not in kaynaklar:
                kaynaklar["yerel_dosyalar"] = {}
            kaynaklar["yerel_dosyalar"][name] = {
                "kaynak": str(kaynak),
                "tarih": datetime.now().isoformat(),
                "hedef": str(hedef),
            }
            _kaynaklari_yaz(kaynaklar)
            print(f"[SkillImport] Skill import edildi: {kaynak.name} -> {hedef}")

        elif islem == "list_sources":
            kaynaklar = _kaynaklari_oku()
            if not kaynaklar:
                print("[SkillImport] Kayitli kaynak yok.")
                return
            print(f"[SkillImport] Kayitli skill kaynaklari:")
            for ad, bilgi in kaynaklar.items():
                if ad == "yerel_dosyalar":
                    print(f"\n  [Yerel Dosyalar]:")
                    for d_ad, d_bilgi in bilgi.items():
                        print(f"    + {d_ad}")
                        print(f"      Kaynak: {d_bilgi.get('kaynak', '?')}")
                        print(f"      Tarih: {d_bilgi.get('tarih', '?')}")
                else:
                    print(f"\n  + {ad}")
                    print(f"    URL: {bilgi.get('url', '?')}")
                    print(f"    Branch: {bilgi.get('branch', '?')}")
                    print(f"    Tarih: {bilgi.get('tarih', '?')}")
                    print(f"    Dosyalar: {bilgi.get('dosya_sayisi', '?')}")
            print(f"\n  Skills klasorunde {len(list(SKILLS_DIR.glob('*.md')))} skill dosyasi var.")

    except Exception as e:
        print(f"[SkillImport] Beklenmeyen hata: {e}")
