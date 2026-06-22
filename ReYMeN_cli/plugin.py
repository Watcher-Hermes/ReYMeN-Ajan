# -*- coding: utf-8 -*-
"""ReYMeN_cli/plugin.py — Plugin yonetimi CLI.

Plugin listeleme, yukleme, kaldirma, etkinlestirme ve devre
disi birakma islemleri.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
PLUGIN_DIR = PROJE_KOK / ".ReYMeN" / "plugins"


def _plugin_listesi() -> list:
    """Yuklu pluginleri listele."""
    if not PLUGIN_DIR.exists():
        return []
    return sorted([p for p in PLUGIN_DIR.iterdir() if p.is_dir() or p.suffix == ".py"])


def kaydet(alt_parser):
    """Plugin CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, install, remove, enable, disable
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "install", "remove", "enable", "disable"],
                            help="Yapilacak islem (list|install|remove|enable|disable)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Plugin adi")
    alt_parser.add_argument("--source", type=str, default=None,
                            help="Plugin kaynagi (install icin)")


def calistir(args):
    """Plugin komutunu calistir."""
    try:
        islem = args.islem or "list"
        PLUGIN_DIR.mkdir(parents=True, exist_ok=True)

        if islem == "list":
            pluginler = _plugin_listesi()
            if not pluginler:
                print("[Plugin] Henuz plugin yuklu degil.")
                return
            print(f"[Plugin] Yuklu pluginler ({len(pluginler)} adet):")
            config_yolu = PLUGIN_DIR / "plugins.json"
            aktif_liste = []
            if config_yolu.exists():
                with open(str(config_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        aktif_liste = json.loads(icerik).get("aktif", [])
            for p in pluginler:
                ad = p.name
                durum = "Aktif" if ad in aktif_liste else "Pasif"
                boyut = sum(f.stat().st_size for f in p.rglob("*")) if p.is_dir() else p.stat().st_size
                print(f"  + {ad} ({boyut}B) [{durum}]")

        elif islem == "install":
            name = args.name
            source = args.source
            if not name:
                print("[Plugin] Lutfen --name parametresini belirtin.")
                return
            hedef = PLUGIN_DIR / name
            if hedef.exists():
                print(f"[Plugin] '{name}' zaten yuklu.")
                return
            if source and os.path.exists(source):
                if os.path.isdir(source):
                    shutil.copytree(source, hedef)
                else:
                    shutil.copy2(source, hedef)
                print(f"[Plugin] Plugin yuklendi: {source} -> {hedef}")
            else:
                hedef.mkdir(parents=True)
                init_yolu = hedef / "__init__.py"
                with open(str(init_yolu), "w", encoding="utf-8") as f:
                    f.write(f'# {name}\n"""Plugin: {name}"""\n\ndef calistir(args):\n    print(f"[{name}] Plugin calistirildi.")\n')
                print(f"[Plugin] Plugin olusturuldu: {hedef}")
            config_yolu = PLUGIN_DIR / "plugins.json"
            config_data = {"aktif": []}
            if config_yolu.exists():
                with open(str(config_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        config_data = json.loads(icerik)
            if name not in config_data["aktif"]:
                config_data["aktif"].append(name)
            with open(str(config_yolu), "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"[Plugin] Plugin etkinlestirildi: {name}")

        elif islem == "remove":
            name = args.name
            if not name:
                print("[Plugin] Lutfen --name parametresini belirtin.")
                return
            hedef = PLUGIN_DIR / name
            if not hedef.exists():
                print(f"[Plugin] Plugin bulunamadi: {name}")
                return
            if hedef.is_dir():
                shutil.rmtree(str(hedef))
            else:
                hedef.unlink()
            config_yolu = PLUGIN_DIR / "plugins.json"
            if config_yolu.exists():
                with open(str(config_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        config_data = json.loads(icerik)
                        if name in config_data.get("aktif", []):
                            config_data["aktif"].remove(name)
                        with open(str(config_yolu), "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2)
            print(f"[Plugin] Plugin kaldirildi: {name}")

        elif islem == "enable":
            name = args.name
            if not name:
                print("[Plugin] Lutfen --name parametresini belirtin.")
                return
            hedef = PLUGIN_DIR / name
            if not hedef.exists():
                print(f"[Plugin] Plugin bulunamadi: {name}")
                return
            config_yolu = PLUGIN_DIR / "plugins.json"
            config_data = {"aktif": []}
            if config_yolu.exists():
                with open(str(config_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        config_data = json.loads(icerik)
            if name not in config_data["aktif"]:
                config_data["aktif"].append(name)
            with open(str(config_yolu), "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"[Plugin] Plugin etkinlestirildi: {name}")

        elif islem == "disable":
            name = args.name
            if not name:
                print("[Plugin] Lutfen --name parametresini belirtin.")
                return
            config_yolu = PLUGIN_DIR / "plugins.json"
            if config_yolu.exists():
                with open(str(config_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        config_data = json.loads(icerik)
                        if name in config_data.get("aktif", []):
                            config_data["aktif"].remove(name)
                        with open(str(config_yolu), "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2)
                        print(f"[Plugin] Plugin devre disi: {name}")
                        return
            print(f"[Plugin] Plugin bulunamadi: {name}")

    except Exception as e:
        print(f"[Plugin] Beklenmeyen hata: {e}")
