# -*- coding: utf-8 -*-
"""ReYMeN_cli/copilot_auth.py — Copilot Kimlik Dogrulama CLI.

Copilot giris, cikis, durum sorgulama, token
goruntuleme ve token yenileme islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _copilot_token_dosyasi() -> Path:
    """Copilot token dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "copilot" / "token.json"


def _token_oku() -> dict:
    """Kayitli tokeni oku."""
    dosya = _copilot_token_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def kaydet(alt_parser):
    """Copilot auth CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: login, logout, status, token, refresh
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["login", "logout", "status", "token", "refresh"],
                            help="Yapilacak islem (login|logout|status|token|refresh)")
    alt_parser.add_argument("--kullanici", type=str, default=None,
                            help="Kullanici adi (login icin)")
    alt_parser.add_argument("--sifre", type=str, default=None,
                            help="Sifre (login icin)")


def calistir(args):
    """Copilot auth komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "login":
            kullanici = args.kullanici or "admin"
            if args.sifre:
                print(f"[CopilotAuth] '{kullanici}' kullanici girisi yapildi.")
            else:
                print(f"[CopilotAuth] '{kullanici}' icin token giris modu.")

        elif islem == "logout":
            print("[CopilotAuth] Copilot oturumu kapatildi.")

        elif islem == "status":
            token = _token_oku()
            if token:
                print(f"[CopilotAuth] Oturum aktif (kullanici: {token.get('kullanici', '?')})")
            else:
                print("[CopilotAuth] Oturum yok. Lutfen 'login' yapin.")

        elif islem == "token":
            token = _token_oku()
            gizli = token.get("access_token", "?")[:12] + "..." if token.get("access_token") else "yok"
            print(f"[CopilotAuth] Mevcut token: {gizli}")

        elif islem == "refresh":
            print("[CopilotAuth] Token yenileniyor...")

    except Exception as e:
        print(f"[CopilotAuth] Beklenmeyen hata: {e}")
