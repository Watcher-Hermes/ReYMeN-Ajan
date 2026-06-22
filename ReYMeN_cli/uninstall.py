# -*- coding: utf-8 -*-
"""ReYMeN_cli/uninstall.py — Kaldirma CLI.

Tool, plugin, skill, gateway, full islemleri.
"""

import json
import os
import shutil
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Uninstall CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: tool, plugin, skill, gateway, full
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["tool", "plugin", "skill", "gateway", "full"],
                            help="Yapilacak islem (tool|plugin|skill|gateway|full)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Kaldirilacak bilesen adi")


def calistir(args):
    """Uninstall komutunu calistir."""
    try:
        islem = args.islem or "list"
        name = args.name

        if islem == "tool":
            if not name:
                print("[Uninstall] Lutfen --name parametresini belirtin.")
                return
            tool_yolu = PROJE_KOK / "ReYMeN_cli" / f"{name}.py"
            if tool_yolu.exists():
                tool_yolu.unlink()
                print(f"[Uninstall] Tool kaldirildi: {name}")
            else:
                print(f"[Uninstall] Tool bulunamadi: {name}")

        elif islem == "plugin":
            if not name:
                print("[Uninstall] Lutfen --name parametresini belirtin.")
                return
            plugin_yolu = PROJE_KOK / "plugins" / f"{name}.py"
            if plugin_yolu.exists():
                plugin_yolu.unlink()
                print(f"[Uninstall] Plugin kaldirildi: {name}")
            else:
                plugin_klasor = PROJE_KOK / "plugins" / name
                if plugin_klasor.exists() and plugin_klasor.is_dir():
                    shutil.rmtree(str(plugin_klasor))
                    print(f"[Uninstall] Plugin kaldirildi: {name}")
                else:
                    print(f"[Uninstall] Plugin bulunamadi: {name}")

        elif islem == "skill":
            if not name:
                print("[Uninstall] Lutfen --name parametresini belirtin.")
                return
            skill_yolu = PROJE_KOK / "skills" / f"{name}.py"
            if skill_yolu.exists():
                skill_yolu.unlink()
                print(f"[Uninstall] Skill kaldirildi: {name}")
            else:
                print(f"[Uninstall] Skill bulunamadi: {name}")

        elif islem == "gateway":
            if not name:
                name = "gateway"
            gateway_yolu = PROJE_KOK / "gateway" / f"{name}.py"
            if gateway_yolu.exists():
                gateway_yolu.unlink()
                print(f"[Uninstall] Gateway kaldirildi: {name}")
            else:
                print(f"[Uninstall] Gateway bulunamadi: {name}")

        elif islem == "full":
            print("[Uninstall] Tam kaldirma baslatiliyor...")
            onay = input("  Tum bilesenler kaldirilsin mi? (e/H): ").strip().lower()
            if onay == "e":
                silinecek = [
                    PROJE_KOK / ".ReYMeN",
                ]
                for yol in silinecek:
                    if yol.exists():
                        shutil.rmtree(str(yol))
                        print(f"  + Silindi: {yol}")
                print("[Uninstall] Tam kaldirma tamam.")
            else:
                print("[Uninstall] Islem iptal edildi.")

    except Exception as e:
        print(f"[Uninstall] Beklenmeyen hata: {e}")
