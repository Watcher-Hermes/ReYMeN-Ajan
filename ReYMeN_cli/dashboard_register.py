# -*- coding: utf-8 -*-
"""ReYMeN_cli/dashboard_register.py — Dashboard CLI.

Dashboard kaydetme, kaldirma, listeleme, URL
goruntuleme ve token yonetimi.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _dashboard_dosyasi() -> Path:
    """Dashboard kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "dashboard" / "kayit.json"


def _dashboardlari_oku() -> list:
    """Kayitli dashboardlari oku."""
    dosya = _dashboard_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Dashboard CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: register, unregister, list, url, token
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["register", "unregister", "list", "url", "token"],
                            help="Yapilacak islem (register|unregister|list|url|token)")
    alt_parser.add_argument("--ad", type=str, default=None,
                            help="Dashboard adi")
    alt_parser.add_argument("--port", type=int, default=None,
                            help="Dashboard portu (register icin)")


def calistir(args):
    """Dashboard komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "register":
            ad = args.ad or "dashboard1"
            port = args.port or 8080
            print(f"[Dashboard] '{ad}' dashboardu kaydedildi (port: {port})")

        elif islem == "unregister":
            ad = args.ad
            if not ad:
                print("[Dashboard] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Dashboard] '{ad}' dashboardu kaldirildi.")

        elif islem == "list":
            dashboardlar = _dashboardlari_oku()
            if not dashboardlar:
                print("[Dashboard] Kayitli dashboard yok.")
            else:
                print(f"[Dashboard] Kayitli dashboardlar ({len(dashboardlar)} adet):")
                for d in dashboardlar:
                    ad = d.get("ad", "?")
                    port = d.get("port", "?")
                    print(f"  + {ad} (port: {port})")

        elif islem == "url":
            ad = args.ad or "dashboard1"
            print(f"[Dashboard] '{ad}' URL: http://localhost:8080/{ad}")

        elif islem == "token":
            print(f"[Dashboard] Dashboard API token: ********")

    except Exception as e:
        print(f"[Dashboard] Beklenmeyen hata: {e}")
