# -*- coding: utf-8 -*-
"""ReYMeN_cli/cron.py — Zamanlanmis gorev CLI.

Cron job'larini listeleme, ekleme, silme, duraklatma, devam ettirme
ve manuel calistirma islemleri.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _cron_joblarini_oku() -> dict:
    """jobs.json'dan cron job'larini oku."""
    jobs_yolu = PROJE_KOK / ".ReYMeN" / "cron" / "jobs.json"
    if not jobs_yolu.exists():
        return {}
    try:
        with open(str(jobs_yolu), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _cron_joblarini_yaz(joblar: dict):
    """jobs.json'a cron job'larini yaz."""
    jobs_yolu = PROJE_KOK / ".ReYMeN" / "cron" / "jobs.json"
    jobs_yolu.parent.mkdir(parents=True, exist_ok=True)
    with open(str(jobs_yolu), "w", encoding="utf-8") as f:
        json.dump(joblar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Cron CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, pause, resume, run
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "pause", "resume", "run"],
                            help="Yapilacak islem (list|add|remove|pause|resume|run)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Job adi")
    alt_parser.add_argument("--command", type=str, default=None,
                            help="Calistirilacak komut")
    alt_parser.add_argument("--schedule", type=str, default=None,
                            help="Cron zamanlamasi")


def calistir(args):
    """Cron komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            joblar = _cron_joblarini_oku()
            if not joblar:
                print("[Cron] Hic cron job'i tanimlanmamis.")
                return
            print(f"[Cron] Zamanlanmis gorevler ({len(joblar)} adet):")
            for isim, bilgi in sorted(joblar.items()):
                komut = bilgi.get("komut", "?")
                zaman = bilgi.get("zaman", "?")
                aktif = bilgi.get("aktif", True)
                durum = "Aktif" if aktif else "Pasif"
                print(f"  + {isim}")
                print(f"    Komut:   {komut}")
                print(f"    Zaman:   {zaman}")
                print(f"    Durum:   {durum}")
                print()

        elif islem == "add":
            name = args.name
            command = args.command
            schedule = args.schedule
            if not name or not command or not schedule:
                print("[Cron] Lutfen --name, --command ve --schedule parametrelerini belirtin.")
                return
            joblar = _cron_joblarini_oku()
            if name in joblar:
                print(f"[Cron] '{name}' zaten var. Uzerine yazilacak.")
            joblar[name] = {
                "komut": command,
                "zaman": schedule,
                "aktif": True,
                "olusturma": datetime.now().isoformat(),
            }
            _cron_joblarini_yaz(joblar)
            print(f"[Cron] Gorev eklendi: {name}")

        elif islem == "remove":
            name = args.name
            if not name:
                print("[Cron] Lutfen --name parametresini belirtin.")
                return
            joblar = _cron_joblarini_oku()
            if name not in joblar:
                print(f"[Cron] Gorev bulunamadi: {name}")
                return
            del joblar[name]
            _cron_joblarini_yaz(joblar)
            print(f"[Cron] Gorev silindi: {name}")

        elif islem == "pause":
            name = args.name
            if not name:
                print("[Cron] Lutfen --name parametresini belirtin.")
                return
            joblar = _cron_joblarini_oku()
            if name not in joblar:
                print(f"[Cron] Gorev bulunamadi: {name}")
                return
            joblar[name]["aktif"] = False
            _cron_joblarini_yaz(joblar)
            print(f"[Cron] Gorev duraklatildi: {name}")

        elif islem == "resume":
            name = args.name
            if not name:
                print("[Cron] Lutfen --name parametresini belirtin.")
                return
            joblar = _cron_joblarini_oku()
            if name not in joblar:
                print(f"[Cron] Gorev bulunamadi: {name}")
                return
            joblar[name]["aktif"] = True
            _cron_joblarini_yaz(joblar)
            print(f"[Cron] Gorev devam ettiriliyor: {name}")

        elif islem == "run":
            name = args.name
            if not name:
                print("[Cron] Lutfen --name parametresini belirtin.")
                return
            joblar = _cron_joblarini_oku()
            if name not in joblar:
                print(f"[Cron] Gorev bulunamadi: {name}")
                return
            komut = joblar[name].get("komut", "")
            print(f"[Cron] Calistiriliyor: {name} -> {komut}")
            try:
                subprocess.run(komut, shell=True, check=True, timeout=60)
                print(f"[Cron] Gorev tamamlandi: {name}")
            except subprocess.CalledProcessError as e:
                print(f"[Cron] Gorev hatasi: {e}")

    except Exception as e:
        print(f"[Cron] Beklenmeyen hata: {e}")
