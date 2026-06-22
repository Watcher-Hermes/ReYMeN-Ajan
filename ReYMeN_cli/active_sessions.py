# -*- coding: utf-8 -*-
"""ReYMeN_cli/active_sessions.py — Aktif Oturum CLI.

Aktif oturumlari listeleme, goruntuleme, baglanma,
ayirma ve sonlandirma islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _session_dosyasi() -> Path:
    """Session bilgilerinin saklandigi dosya yolu."""
    return PROJE_KOK / ".ReYMeN" / "sessions" / "aktif.json"


def _sessionlari_oku() -> list:
    """Kayitli aktif sessionlari oku."""
    dosya = _session_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Aktif oturum CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, view, attach, detach, kill
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "view", "attach", "detach", "kill"],
                            help="Yapilacak islem (list|view|attach|detach|kill)")
    alt_parser.add_argument("--id", type=str, default=None,
                            help="Oturum ID (view/attach/detach/kill icin)")
    alt_parser.add_argument("--force", action="store_true",
                            help="Zorla sonlandir (kill icin)")


def calistir(args):
    """Aktif oturum komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            sessionlar = _sessionlari_oku()
            if not sessionlar:
                print("[ActiveSessions] Aktif oturum yok.")
            else:
                print(f"[ActiveSessions] Aktif oturumlar ({len(sessionlar)} adet):")
                for s in sessionlar:
                    sid = s.get("id", "?")
                    tip = s.get("tip", "?")
                    bas = s.get("baslangic", "?")
                    print(f"  + {sid} [{tip}] baslangic: {bas}")

        elif islem == "view":
            sid = args.id
            if not sid:
                print("[ActiveSessions] Lutfen --id parametresini belirtin.")
                return
            sessionlar = _sessionlari_oku()
            for s in sessionlar:
                if s.get("id") == sid:
                    print(f"[ActiveSessions] Oturum: {json.dumps(s, indent=2, ensure_ascii=False)}")
                    return
            print(f"[ActiveSessions] '{sid}' ID'li oturum bulunamadi.")

        elif islem == "attach":
            sid = args.id
            if not sid:
                print("[ActiveSessions] Lutfen --id parametresini belirtin.")
                return
            print(f"[ActiveSessions] '{sid}' oturumuna baglaniliyor...")

        elif islem == "detach":
            sid = args.id
            if not sid:
                print("[ActiveSessions] Lutfen --id parametresini belirtin.")
                return
            print(f"[ActiveSessions] '{sid}' oturumundan ayrililiyor...")

        elif islem == "kill":
            sid = args.id
            if not sid:
                print("[ActiveSessions] Lutfen --id parametresini belirtin.")
                return
            force = args.force
            print(f"[ActiveSessions] '{sid}' oturumu {'zorla ' if force else ''}sonlandiriliyor...")

    except Exception as e:
        print(f"[ActiveSessions] Beklenmeyen hata: {e}")
