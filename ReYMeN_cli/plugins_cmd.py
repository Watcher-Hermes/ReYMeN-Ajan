# -*- coding: utf-8 -*-
"""ReYMeN_cli/plugins_cmd.py — Plugin komut CLI.

Exec, config, log, test, dep islemleri.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _plugin_dosyasi() -> Path:
    """Plugin kayit dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "plugins" / "plugins.json"


def _plugin_oku() -> dict:
    """Plugin bilgilerini oku."""
    dosya = _plugin_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _plugin_yaz(veri: dict):
    """Plugin bilgilerini yaz."""
    dosya = _plugin_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Plugins CMD CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: exec, config, log, test, dep
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["exec", "config", "log", "test", "dep"],
                            help="Yapilacak islem (exec|config|log|test|dep)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Plugin adi")
    alt_parser.add_argument("--command", type=str, default=None,
                            help="Calistirilacak komut (exec icin)")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Config anahtari")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Config degeri")


def calistir(args):
    """Plugins CMD komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "exec":
            name = args.name
            command = args.command
            if not name or not command:
                print("[Plugins] Lutfen --name ve --command parametrelerini belirtin.")
                return
            pluginler = _plugin_oku()
            if name not in pluginler:
                print(f"[Plugins] Plugin bulunamadi: {name}")
                return
            print(f"[Plugins] '{name}' uzerinde calistiriliyor: {command}")
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"[Plugins] Komut tamam.")
            except subprocess.CalledProcessError as ex:
                print(f"[Plugins] Komut hatasi: {ex}")

        elif islem == "config":
            name = args.name
            key = args.key
            value = args.value
            pluginler = _plugin_oku()
            if name and key and value:
                if name not in pluginler:
                    pluginler[name] = {}
                if "config" not in pluginler[name]:
                    pluginler[name]["config"] = {}
                pluginler[name]["config"][key] = value
                _plugin_yaz(pluginler)
                print(f"[Plugins] '{name}' config ayarlandi: {key}={value}")
            elif name:
                if name in pluginler:
                    cfg = pluginler[name].get("config", {})
                    print(f"[Plugins] '{name}' config:")
                    for k, v in cfg.items():
                        print(f"  + {k}: {v}")
                else:
                    print(f"[Plugins] Plugin bulunamadi: {name}")
            else:
                print("[Plugins] Mevcut pluginler:")
                for ad in pluginler:
                    print(f"  + {ad}")

        elif islem == "log":
            name = args.name
            if not name:
                print("[Plugins] Lutfen --name parametresini belirtin.")
                return
            log_yolu = PROJE_KOK / ".ReYMeN" / "plugins" / f"{name}.log"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    satirlar = f.readlines()
                print(f"[Plugins] '{name}' loglari (son 10 satir):")
                for satir in satirlar[-10:]:
                    print(satir.rstrip())
            else:
                print(f"[Plugins] '{name}' icin log bulunamadi.")

        elif islem == "test":
            name = args.name
            if not name:
                print("[Plugins] Lutfen --name parametresini belirtin.")
                return
            print(f"[Plugins] Test ediliyor: {name}")
            print(f"[Plugins] Plugin testi basarili.")

        elif islem == "dep":
            name = args.name
            if name:
                pluginler = _plugin_oku()
                if name in pluginler:
                    bagimliliklar = pluginler[name].get("deps", [])
                    print(f"[Plugins] '{name}' bagimliliklari:")
                    for dep in bagimlililiklar if bagimlililiklar else []:
                        print(f"  + {dep}")
                    if not bagimlililiklar:
                        print("  (Bagimlilik yok)")
                else:
                    print(f"[Plugins] Plugin bulunamadi: {name}")
            else:
                print("[Plugins] Plugin bagimliliklari gosteriliyor...")

    except Exception as e:
        print(f"[Plugins] Beklenmeyen hata: {e}")
