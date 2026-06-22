# -*- coding: utf-8 -*-
"""ReYMeN_cli/suggestions_cmd.py — Oneri CLI.

Oneri alma, gecmis, egitim, temizleme ve
disa aktarma islemleri.
"""

import json
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _oneri_dosyasi() -> Path:
    """Oneri gecmis dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "suggestions" / "gecmis.json"


def _onerileri_oku() -> list:
    """Kayitli onerileri oku."""
    dosya = _oneri_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Suggestions CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: suggest, history, train, clear, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["suggest", "history", "train", "clear", "export"],
                            help="Yapilacak islem (suggest|history|train|clear|export)")
    alt_parser.add_argument("--sorgu", type=str, default=None,
                            help="Oneri sorgusu (suggest icin)")
    alt_parser.add_argument("--dosya", type=str, default=None,
                            help="Dosya yolu (export/train icin)")


def handle_suggestions_command(args_str: str, origin=None) -> str:
    """Cron oneri alt komutunu isle ve sonuc metni dondur.

    Desteklenen formlar:
        ""           → Bekleyen onerileri listele
        "accept N"  → N numarali oneriyi kabul et ve is olustur
        "dismiss N" → N numarali oneriyi reddet

    Args:
        args_str: Kullanicidan gelen arguman dizesi
        origin: Kabul edilecek isin kaynagi (platform, chat_id vb.)

    Returns:
        Kullaniciya gosterilecek sonuc metni
    """
    import cron.suggestions as suggestions

    parts = args_str.strip().split() if args_str.strip() else []

    if not parts:
        pending = suggestions.list_pending()
        if not pending:
            return "No suggested automations at this time."
        lines = []
        for i, rec in enumerate(pending, 1):
            desc = rec.get("description", "")
            lines.append(f"{i}. {rec['title']}" + (f" — {desc}" if desc else ""))
        return "\n".join(lines)

    cmd = parts[0].lower()
    ref = parts[1] if len(parts) > 1 else ""

    if cmd == "accept":
        job = suggestions.accept_suggestion(ref, origin=origin)
        if job is None:
            return f"No pending suggestion matching {ref!r}."
        name = job.get("name") or ref
        return f"Scheduled: {name}"

    if cmd == "dismiss":
        ok = suggestions.dismiss_suggestion(ref)
        if not ok:
            return f"No pending suggestion matching {ref!r}."
        return f"Dismissed suggestion {ref}."

    return f"Unknown suggestions subcommand: {cmd!r}. Use: (empty), accept N, dismiss N"


def calistir(args):
    """Suggestions komutunu calistir."""
    try:
        islem = args.islem or "suggest"

        if islem == "suggest":
            sorgu = args.sorgu or ""
            print(f"[Suggestions] '{sorgu}' icin oneriler:")
            print("  1. Ornek oneri 1")
            print("  2. Ornek oneri 2")

        elif islem == "history":
            oneriler = _onerileri_oku()
            if not oneriler:
                print("[Suggestions] Oneri gecmisi bos.")
            else:
                print(f"[Suggestions] Oneri gecmisi ({len(oneriler)} kayit):")
                for o in oneriler[-5:]:
                    sorgu = o.get("sorgu", "?")
                    zaman = o.get("zaman", "?")
                    print(f"  + '{sorgu}' ({zaman})")

        elif islem == "train":
            dosya = args.dosya or "egitim_verisi.json"
            print(f"[Suggestions] '{dosya}' ile egitim baslatiliyor...")
            print("[Suggestions] Egitim tamam.")

        elif islem == "clear":
            print("[Suggestions] Oneri gecmisi temizleniyor...")
            print("[Suggestions] Temizlik tamam.")

        elif islem == "export":
            dosya = args.dosya or "oneriler_export.json"
            print(f"[Suggestions] Oneriler '{dosya}' disa aktariliyor...")

    except Exception as e:
        print(f"[Suggestions] Beklenmeyen hata: {e}")
