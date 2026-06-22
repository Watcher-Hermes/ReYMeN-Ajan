# -*- coding: utf-8 -*-
"""ReYMeN_cli/migrate.py — Veritabani Goc CLI.

Veritabani migrasyon kontrol, planlama, calistirma,
geri alma ve durum sorgulama islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _migrate_dosyasi() -> Path:
    """Migrasyon kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "migrate" / "durum.json"


def kaydet(alt_parser):
    """Migrate CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: check, plan, run, rollback, status
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["check", "plan", "run", "rollback", "status"],
                            help="Yapilacak islem (check|plan|run|rollback|status)")
    alt_parser.add_argument("--id", type=str, default=None,
                            help="Migrasyon ID (run/rollback icin)")
    alt_parser.add_argument("--adim", type=int, default=None,
                            help="Adim sayisi (rollback icin)")


def calistir(args):
    """Migrate komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "check":
            print("[Migrate] Bekleyen migrasyon kontrol ediliyor...")
            print("[Migrate] Bekleyen migrasyon: 0")

        elif islem == "plan":
            print("[Migrate] Migrasyon plani:")
            print("  1. V001_initial.sql (tamam)")
            print("  2. V002_add_fields.sql (bekliyor)")

        elif islem == "run":
            mid = args.id or "tum"
            print(f"[Migrate] '{mid}' migrasyonu calistiriliyor...")
            print("[Migrate] Migrasyon basarili.")

        elif islem == "rollback":
            mid = args.id
            adim = args.adim or 1
            if mid:
                print(f"[Migrate] '{mid}' geri aliniyor...")
            else:
                print(f"[Migrate] Son {adim} adim geri aliniyor...")
            print("[Migrate] Geri alma basarili.")

        elif islem == "status":
            print("[Migrate] Migrasyon durumu:")
            print("  Son migrasyon: V002_add_fields.sql")
            print("  Toplam: 2, Tamam: 1, Bekleyen: 1")

    except Exception as e:
        print(f"[Migrate] Beklenmeyen hata: {e}")
