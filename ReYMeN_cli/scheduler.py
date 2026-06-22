# -*- coding: utf-8 -*-
"""ReYMeN_cli/scheduler.py — Zamanlayici CLI.

Gorev zamanlama, cron yonetimi ve periyodik islemler.
"""

import json
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
CRON_DIZIN = PROJE_KOK / ".ReYMeN" / "cron"


def _gorev_listesi():
    """Kayitli cron gorevleri."""
    gorevler = {}
    jobs_yolu = CRON_DIZIN / "jobs.json"
    if jobs_yolu.exists():
        with open(str(jobs_yolu), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            if icerik:
                gorevler = json.loads(icerik)
    if not gorevler:
        gorevler = {"ornek": {"komut": "test", "zaman": "* * * * *", "aktif": False}}
    return gorevler


def kaydet(alt_parser):
    """scheduler CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "enable", "disable"],
                            help="Yapilacak islem (list|add|remove|enable|disable)")
    alt_parser.add_argument("--name", type=str, default=None, help="Gorev adi")
    alt_parser.add_argument("--command", type=str, default=None, help="Calisacak komut")
    alt_parser.add_argument("--cron", type=str, default=None, help="Cron ifadesi")
    alt_parser.add_argument("--at", type=str, default=None, help="Zaman (HH:MM)")


def calistir(args):
    """scheduler komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Scheduler] Baslatiliyor: {islem}")

        if islem == "list":
            gorevler = _gorev_listesi()
            print("[Scheduler] Zamanli gorevler:")
            for ad, bilgi in gorevler.items():
                durum = "AKTIF" if bilgi.get("aktif") else "PASIF"
                print(f"  [{durum}] {ad}: {bilgi.get('komut', '?')} ({bilgi.get('zaman', '-')})")

        elif islem == "add":
            ad = args.name or "yeni_gorev"
            komut = args.command or "echo test"
            cron = args.cron or "0 * * * *"
            CRON_DIZIN.mkdir(parents=True, exist_ok=True)
            gorevler = _gorev_listesi()
            gorevler[ad] = {
                "komut": komut,
                "zaman": cron,
                "aktif": True,
                "olusturma": datetime.now().isoformat(),
            }
            with open(str(CRON_DIZIN / "jobs.json"), "w", encoding="utf-8") as f:
                json.dump(gorevler, f, indent=2, ensure_ascii=False)
            print(f"[Scheduler] Gorev eklendi: {ad} ({cron})")

        elif islem == "remove":
            ad = args.name
            if ad:
                gorevler = _gorev_listesi()
                if ad in gorevler:
                    del gorevler[ad]
                    with open(str(CRON_DIZIN / "jobs.json"), "w", encoding="utf-8") as f:
                        json.dump(gorevler, f, indent=2)
                    print(f"[Scheduler] Gorev silindi: {ad}")
                else:
                    print(f"[Scheduler] Gorev bulunamadi: {ad}")
            else:
                print("[Scheduler] --name belirtin")

        elif islem == "enable":
            ad = args.name or "tum"
            print(f"[Scheduler] Aktif ediliyor: {ad}")

        elif islem == "disable":
            ad = args.name or "tum"
            print(f"[Scheduler] Devre disi birakiliyor: {ad}")

    except Exception as e:
        print(f"[Scheduler] Hata: {e}")
