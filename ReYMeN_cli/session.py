# -*- coding: utf-8 -*-
"""ReYMeN_cli/session.py — Oturum CLI.

Oturum listeleme, goruntuleme, arama, disa aktarma ve silme islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _oturum_kayitlari() -> list:
    """Kayitli oturum dosyalarini bul."""
    kaynaklar = [
        PROJE_KOK / "logs",
        PROJE_KOK / ".ReYMeN" / "sessions",
    ]
    dosyalar = []
    for k in kaynaklar:
        if k.exists():
            for f in k.iterdir():
                if f.suffix in (".json", ".log", ".txt") and f.is_file():
                    dosyalar.append(f)
    return sorted(dosyalar, key=lambda x: x.stat().st_mtime, reverse=True)


def kaydet(alt_parser):
    """Session CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, view, search, export, delete
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "view", "search", "export", "delete"],
                            help="Yapilacak islem (list|view|search|export|delete)")
    alt_parser.add_argument("--id", type=str, default=None,
                            help="Oturum ID'si")
    alt_parser.add_argument("--query", type=str, default=None,
                            help="Arama sorgusu")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (export icin)")


def calistir(args):
    """Session komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            oturumlar = _oturum_kayitlari()
            if not oturumlar:
                print("[Session] Kayitli oturum bulunamadi.")
                return
            print(f"[Session] Oturumlar ({len(oturumlar)} adet):")
            for i, oturum in enumerate(oturumlar[:20], 1):
                boyut = oturum.stat().st_size
                mtime = datetime.fromtimestamp(oturum.stat().st_mtime)
                print(f"  {i:2d}. {oturum.name} ({boyut}B, {mtime.strftime('%d.%m.%Y %H:%M')})")
                print(f"       {oturum.parent.name}/{oturum.name}")

        elif islem == "view":
            session_id = args.id
            if not session_id:
                oturumlar = _oturum_kayitlari()
                if oturumlar:
                    session_id = oturumlar[0].name
                    print(f"[Session] Son oturum: {session_id}")
                else:
                    print("[Session] Goruntulenecek oturum yok.")
                    return
            for kaynak_dizin in [PROJE_KOK / "logs", PROJE_KOK / ".ReYMeN" / "sessions"]:
                if kaynak_dizin.exists():
                    for f in kaynak_dizin.iterdir():
                        if f.name == session_id or f.stem == session_id:
                            with open(str(f), "r", encoding="utf-8") as fh:
                                print(fh.read()[:2000])
                            return
            print(f"[Session] Oturum bulunamadi: {session_id}")

        elif islem == "search":
            query = args.query
            if not query:
                print("[Session] Lutfen --query parametresini belirtin.")
                return
            oturumlar = _oturum_kayitlari()
            print(f"[Session] Araniyor: {query}")
            bulunan = 0
            for oturum in oturumlar:
                try:
                    with open(str(oturum), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    if query.lower() in icerik.lower():
                        print(f"  + {oturum.name} ({oturum.parent.name})")
                        bulunan += 1
                        if bulunan >= 10:
                            break
                except Exception:
                    continue
            if bulunan == 0:
                print(f"  Eslesme bulunamadi: {query}")
            else:
                print(f"  {bulunan} oturumda eslesme bulundu.")

        elif islem == "export":
            session_id = args.id
            cikti = args.output or str(PROJE_KOK / "session_export.json")
            if not session_id:
                print("[Session] Lutfen --id parametresini belirtin.")
                return
            for kaynak_dizin in [PROJE_KOK / "logs", PROJE_KOK / ".ReYMeN" / "sessions"]:
                if kaynak_dizin.exists():
                    for f in kaynak_dizin.iterdir():
                        if f.name == session_id or f.stem == session_id:
                            try:
                                with open(str(f), "r", encoding="utf-8") as fh:
                                    icerik = fh.read()
                                export_data = {
                                    "session_id": session_id,
                                    "kaynak": str(f),
                                    "tarih": datetime.now().isoformat(),
                                    "icerik": icerik,
                                }
                                with open(cikti, "w", encoding="utf-8") as out:
                                    json.dump(export_data, out, indent=2, ensure_ascii=False)
                                print(f"[Session] Oturum export edildi: {cikti}")
                                return
                            except Exception as e:
                                print(f"[Session] Export hatasi: {e}")
                                return
            print(f"[Session] Oturum bulunamadi: {session_id}")

        elif islem == "delete":
            session_id = args.id
            if not session_id:
                print("[Session] Lutfen --id parametresini belirtin.")
                return
            silindi = False
            for kaynak_dizin in [PROJE_KOK / "logs", PROJE_KOK / ".ReYMeN" / "sessions"]:
                if kaynak_dizin.exists():
                    for f in kaynak_dizin.iterdir():
                        if f.name == session_id or f.stem == session_id:
                            f.unlink()
                            print(f"[Session] Silindi: {f.name}")
                            silindi = True
                            break
            if not silindi:
                print(f"[Session] Oturum bulunamadi: {session_id}")

    except Exception as e:
        print(f"[Session] Beklenmeyen hata: {e}")
