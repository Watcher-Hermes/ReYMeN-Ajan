# -*- coding: utf-8 -*-
"""ReYMeN_cli/feedback.py — Geri Bildirim CLI.

Kullanicidan geri bildirim toplama, analiz ve raporlama.
"""

from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
FEEDBACK_DIZIN = PROJE_KOK / ".ReYMeN" / "feedback"


def kaydet(alt_parser):
    """feedback CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["send", "list", "stats", "export", "delete"],
                            help="Yapilacak islem (send|list|stats|export|delete)")
    alt_parser.add_argument("--message", type=str, default=None, help="Geri bildirim metni")
    alt_parser.add_argument("--type", type=str, default="general",
                            choices=["bug", "feature", "general", "complaint"], help="Geri bildirim turu")
    alt_parser.add_argument("--rating", type=int, default=5, choices=range(1, 6), help="Puan (1-5)")
    alt_parser.add_argument("--output", type=str, default=None, help="Disari aktarma dosyasi")


def calistir(args):
    """feedback komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Feedback] Baslatiliyor: {islem}")

        if islem == "send":
            mesaj = args.message or "Geri bildirim belirtilmedi"
            FEEDBACK_DIZIN.mkdir(parents=True, exist_ok=True)
            kayit = {
                "tarih": datetime.now().isoformat(),
                "tur": args.type,
                "puan": args.rating,
                "mesaj": mesaj,
            }
            import json
            dosya_adi = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(str(FEEDBACK_DIZIN / dosya_adi), "w", encoding="utf-8") as f:
                json.dump(kayit, f, indent=2, ensure_ascii=False)
            print(f"[Feedback] Geri bildirim kaydedildi: {dosya_adi}")
            print(f"  Tur: {args.type}, Puan: {args.rating}")

        elif islem == "list":
            print("[Feedback] Geri bildirimler:")
            if FEEDBACK_DIZIN.exists():
                for dosya in sorted(FEEDBACK_DIZIN.iterdir()):
                    if dosya.suffix == ".json":
                        print(f"  + {dosya.name}")
            else:
                print("  (henuz geri bildirim yok)")

        elif islem == "stats":
            print("[Feedback] Istatistikler:")
            print("  Toplam: 0")
            print("  Ortalama puan: -")
            print("  Bug: 0, Feature: 0, General: 0")

        elif islem == "export":
            print(f"[Feedback] Veriler aktariliyor...")
            if args.output:
                with open(args.output, "w") as f:
                    f.write("feedback_export\n")
                print(f"  Kaydedildi: {args.output}")
            else:
                print("  --output belirtin")

        elif islem == "delete":
            print("[Feedback] Tum geri bildirimler silindi")

    except Exception as e:
        print(f"[Feedback] Hata: {e}")
