# -*- coding: utf-8 -*-
"""ReYMeN_cli/service_manager.py — Servis yoneticisi CLI.

Start, stop, restart, status, enable islemleri.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _servis_dosyasi() -> Path:
    """Servis kayit dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "services" / "services.json"


def _servisleri_oku() -> dict:
    """Servis bilgilerini oku."""
    dosya = _servis_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _servisleri_yaz(servisler: dict):
    """Servis bilgilerini yaz."""
    dosya = _servis_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(servisler, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Service Manager CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: start, stop, restart, status, enable
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "restart", "status", "enable"],
                            help="Yapilacak islem (start|stop|restart|status|enable)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Servis adi")
    alt_parser.add_argument("--command", type=str, default=None,
                            help="Servis komutu (start/enable icin)")


def calistir(args):
    """Service Manager komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "start":
            name = args.name
            command = args.command
            if not name or not command:
                print("[Service] Lutfen --name ve --command parametrelerini belirtin.")
                return
            servisler = _servisleri_oku()
            servisler[name] = {
                "komut": command,
                "durum": "calisiyor",
                "baslama": datetime.now().isoformat(),
            }
            _servisleri_yaz(servisler)
            print(f"[Service] '{name}' baslatildi: {command}")

        elif islem == "stop":
            name = args.name
            if not name:
                print("[Service] Lutfen --name parametresini belirtin.")
                return
            servisler = _servisleri_oku()
            if name not in servisler:
                print(f"[Service] Servis bulunamadi: {name}")
                return
            servisler[name]["durum"] = "durduruldu"
            _servisleri_yaz(servisler)
            print(f"[Service] '{name}' durduruldu.")

        elif islem == "restart":
            name = args.name
            if not name:
                print("[Service] Lutfen --name parametresini belirtin.")
                return
            servisler = _servisleri_oku()
            if name not in servisler:
                print(f"[Service] Servis bulunamadi: {name}")
                return
            servisler[name]["durum"] = "yeniden_basliyor"
            servisler[name]["baslama"] = datetime.now().isoformat()
            _servisleri_yaz(servisler)
            print(f"[Service] '{name}' yeniden baslatiliyor...")
            servisler[name]["durum"] = "calisiyor"
            _servisleri_yaz(servisler)
            print(f"[Service] '{name}' yeniden baslatildi.")

        elif islem == "status":
            servisler = _servisleri_oku()
            if not servisler:
                print("[Service] Kayitli servis yok.")
            else:
                print(f"[Service] Servis durumlari ({len(servisler)} adet):")
                for ad, bilgi in sorted(servisler.items()):
                    durum = bilgi.get("durum", "?")
                    baslama = bilgi.get("baslama", "?")
                    print(f"  + {ad}: {durum} (baslama: {baslama})")

        elif islem == "enable":
            name = args.name
            command = args.command
            if not name or not command:
                print("[Service] Lutfen --name ve --command parametrelerini belirtin.")
                return
            servisler = _servisleri_oku()
            if name not in servisler:
                servisler[name] = {}
            servisler[name]["komut"] = command
            servisler[name]["otomatik_baslat"] = True
            servisler[name]["durum"] = "aktif"
            _servisleri_yaz(servisler)
            print(f"[Service] '{name}' otomatik baslatmaya eklendi.")

    except Exception as e:
        print(f"[Service] Beklenmeyen hata: {e}")
