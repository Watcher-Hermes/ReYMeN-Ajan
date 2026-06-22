# -*- coding: utf-8 -*-
"""ReYMeN_cli/backup.py — Yedekleme CLI.

Yedek olusturma, geri yukleme, listeleme ve zamanlama islemleri.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
BACKUP_DIR = PROJE_KOK / "backups"


def _backup_listesi():
    """Kayitli yedekleri oku."""
    BACKUP_DIR.mkdir(exist_ok=True)
    liste = []
    for dosya in sorted(BACKUP_DIR.iterdir()):
        if dosya.suffix in (".zip", ".tar", ".gz", ".bak"):
            boyut = dosya.stat().st_size
            liste.append((dosya.name, boyut, datetime.fromtimestamp(dosya.stat().st_mtime)))
    return liste


def kaydet(alt_parser):
    """Backup CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: create, restore, list, schedule
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["create", "restore", "list", "schedule"],
                            help="Yapilacak islem (create|restore|list|schedule)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Yedek adi")
    alt_parser.add_argument("--source", type=str, default=None,
                            help="Yedeklenecek kaynak dizin/dosya")
    alt_parser.add_argument("--cron", type=str, default=None,
                            help="Zamanlama ifadesi (schedule icin)")


def calistir(args):
    """Backup komutunu calistir."""
    try:
        islem = args.islem or "list"
        BACKUP_DIR.mkdir(exist_ok=True)

        if islem == "create":
            name = args.name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            kaynak = args.source
            if not kaynak:
                kaynak = str(PROJE_KOK / ".ReYMeN")
            hedef = BACKUP_DIR / f"{name}.zip"
            print(f"[Backup] Yedek olusturuluyor: {name}")
            shutil.make_archive(str(BACKUP_DIR / name), "zip", kaynak)
            print(f"[Backup] Yedek tamam: {hedef}")

        elif islem == "restore":
            name = args.name
            if not name:
                print("[Backup] Lutfen --name parametresini belirtin.")
                return
            kaynak_zip = BACKUP_DIR / name
            if not kaynak_zip.exists():
                kaynak_zip = BACKUP_DIR / f"{name}.zip"
            if not kaynak_zip.exists():
                print(f"[Backup] Yedek bulunamadi: {name}")
                return
            hedef = args.source or str(PROJE_KOK / ".ReYMeN_restored")
            print(f"[Backup] Geri yukleniyor: {kaynak_zip} -> {hedef}")
            shutil.unpack_archive(str(kaynak_zip), hedef)
            print(f"[Backup] Geri yukleme tamam.")

        elif islem == "list":
            yedekler = _backup_listesi()
            if not yedekler:
                print("[Backup] Henuz yedek yok.")
            else:
                print(f"[Backup] Kayitli yedekler ({len(yedekler)} adet):")
                for ad, boyut, tarih in yedekler:
                    print(f"  + {ad} ({boyut}B, {tarih.strftime('%d.%m.%Y %H:%M')})")

        elif islem == "schedule":
            cron_ifade = args.cron
            if cron_ifade:
                jobs_yolu = PROJE_KOK / ".ReYMeN" / "cron" / "jobs.json"
                jobs_yolu.parent.mkdir(parents=True, exist_ok=True)
                joblar = {}
                if jobs_yolu.exists():
                    with open(str(jobs_yolu), "r", encoding="utf-8") as f:
                        icerik = f.read().strip()
                        if icerik:
                            joblar = json.loads(icerik)
                joblar["backup"] = {
                    "komut": "backup create",
                    "zaman": cron_ifade,
                    "aktif": True,
                    "olusturma": datetime.now().isoformat(),
                }
                with open(str(jobs_yolu), "w", encoding="utf-8") as f:
                    json.dump(joblar, f, indent=2, ensure_ascii=False)
                print(f"[Backup] Zamanli yedekleme ayarlandi: {cron_ifade}")
            else:
                print("[Backup] Mevcut zamanlama ayarlari gosteriliyor...")

    except Exception as e:
        print(f"[Backup] Beklenmeyen hata: {e}")
