# -*- coding: utf-8 -*-
"""ReYMeN_cli/inventory.py — Envanter CLI.

Tools, plugins, skills, gateway, all islemleri.
"""

import json
import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _dizin_listele(klasor: str) -> list:
    """Bir klasordeki .py dosyalarini listele."""
    yol = PROJE_KOK / klasor
    if not yol.exists():
        return []
    return [d.name for d in sorted(yol.iterdir()) if d.suffix == ".py"]


def kaydet(alt_parser):
    """Inventory CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: tools, plugins, skills, gateway, all
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["tools", "plugins", "skills", "gateway", "all"],
                            help="Yapilacak islem (tools|plugins|skills|gateway|all)")
    alt_parser.add_argument("--detail", action="store_true",
                            help="Detayli liste")


def calistir(args):
    """Inventory komutunu calistir."""
    try:
        islem = args.islem or "all"
        detay = args.detail

        if islem in ("tools", "all"):
            print("[Inventory] Araclar:")
            arac_sayisi = len(_dizin_listele("ReYMeN_cli"))
            print(f"  + CLI modulleri: {arac_sayisi} adet")
            if detay:
                for m in _dizin_listele("ReYMeN_cli"):
                    print(f"    - {m}")

        if islem in ("plugins", "all"):
            print("\n[Inventory] Pluginler:")
            pluginler = _dizin_listele("plugins")
            if pluginler:
                print(f"  + Plugin sayisi: {len(pluginler)}")
                if detay:
                    for p in pluginler:
                        print(f"    - {p}")
            else:
                print("  + Plugin bulunamadi.")

        if islem in ("skills", "all"):
            print("\n[Inventory] Skill'ler:")
            skill_listesi = _dizin_listele("skills")
            if skill_listesi:
                print(f"  + Skill sayisi: {len(skill_listesi)}")
                if detay:
                    for s in skill_listesi:
                        print(f"    - {s}")
            else:
                print("  + Skill bulunamadi.")

        if islem in ("gateway", "all"):
            print("\n[Inventory] Gateway:")
            gateway_dosyasi = PROJE_KOK / "gateway" / "gateway.py"
            if gateway_dosyasi.exists():
                print("  + Gateway mevcut")
            else:
                print("  + Gateway bulunamadi.")

        if islem == "all":
            print("\n[Inventory] Toplam ozet:")
            toplam = 0
            for kat in ["ReYMeN_cli", "plugins", "skills"]:
                adet = len(_dizin_listele(kat))
                toplam += adet
            print(f"  + Toplam bilesen: {toplam}")

    except Exception as e:
        print(f"[Inventory] Beklenmeyen hata: {e}")
