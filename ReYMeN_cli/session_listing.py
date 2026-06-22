# -*- coding: utf-8 -*-
"""ReYMeN_cli/session_listing.py — Oturum listeleme CLI.

Active, history, search, export, clean islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _session_dosyasi() -> Path:
    """Session kayit dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "sessions" / "sessions.json"


def _sessionlari_oku() -> dict:
    """Kayitli oturumlari oku."""
    dosya = _session_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _sessionlari_yaz(sessionlar: dict):
    """Oturumlari dosyaya yaz."""
    dosya = _session_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(sessionlar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Session Listing CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: active, history, search, export, clean
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["active", "history", "search", "export", "clean"],
                            help="Yapilacak islem (active|history|search|export|clean)")
    alt_parser.add_argument("--query", type=str, default=None,
                            help="Arama metni (search icin)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (export icin)")
    alt_parser.add_argument("--days", type=int, default=30,
                            help="Kac gun oncesi (clean icin)")


def calistir(args):
    """Session Listing komutunu calistir."""
    try:
        islem = args.islem or "active"

        if islem == "active":
            sessionlar = _sessionlari_oku()
            aktifler = {k: v for k, v in sessionlar.items() if v.get("durum") == "aktif"}
            if not aktifler:
                print("[Session] Aktif oturum yok.")
            else:
                print(f"[Session] Aktif oturumlar ({len(aktifler)} adet):")
                for sid, bilgi in sorted(aktifler.items()):
                    baslama = bilgi.get("baslama", "?")
                    print(f"  + {sid}: baslama={baslama}")

        elif islem == "history":
            sessionlar = _sessionlari_oku()
            if not sessionlar:
                print("[Session] Kayitli oturum yok.")
            else:
                print(f"[Session] Oturum gecmisi ({len(sessionlar)} adet):")
                for sid, bilgi in sorted(sessionlar.items(), key=lambda x: x[1].get("baslama", ""), reverse=True)[:20]:
                    durum = bilgi.get("durum", "?")
                    baslama = bilgi.get("baslama", "?")
                    print(f"  + {sid}: {durum} ({baslama})")

        elif islem == "search":
            query = args.query
            if not query:
                print("[Session] Lutfen --query parametresini belirtin.")
                return
            sessionlar = _sessionlari_oku()
            eslesenler = {k: v for k, v in sessionlar.items() if query.lower() in k.lower()}
            if not eslesenler:
                print(f"[Session] '{query}' icin eslesme bulunamadi.")
            else:
                print(f"[Session] '{query}' icin {len(eslesenler)} eslesme:")
                for sid in sorted(eslesenler.keys()):
                    print(f"  + {sid}")

        elif islem == "export":
            sessionlar = _sessionlari_oku()
            output = args.output or str(PROJE_KOK / ".ReYMeN" / "sessions" / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output, "w", encoding="utf-8") as f:
                json.dump(sessionlar, f, indent=2, ensure_ascii=False)
            print(f"[Session] Export edildi: {output} ({len(sessionlar)} kayit)")

        elif islem == "clean":
            days = args.days or 30
            sessionlar = _sessionlari_oku()
            simdi = datetime.now()
            silinen = 0
            temiz_sessionlar = {}
            for sid, bilgi in sessionlar.items():
                try:
                    baslama = datetime.fromisoformat(bilgi.get("baslama", ""))
                    fark = (simdi - baslama).days
                    if fark <= days:
                        temiz_sessionlar[sid] = bilgi
                    else:
                        silinen += 1
                except Exception:
                    temiz_sessionlar[sid] = bilgi
            _sessionlari_yaz(temiz_sessionlar)
            print(f"[Session] Temizlendi: {silinen} eski oturum silindi, {len(temiz_sessionlar)} kaldi.")

    except Exception as e:
        print(f"[Session] Beklenmeyen hata: {e}")
