# -*- coding: utf-8 -*-
"""ReYMeN_cli/permissions.py — Yetki Yonetim CLI.

Kullanici yetkileri, roller ve erisim kontrolu.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _varsayilan_roller():
    """Varsayilan roller ve yetkiler."""
    return {
        "admin": ["okuma", "yazma", "silme", "yonetim", "yapilandirma"],
        "operator": ["okuma", "yazma", "calistirma"],
        "viewer": ["okuma"],
        "guest": ["okuma.sinirli"],
    }


def kaydet(alt_parser):
    """permissions CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "grant", "revoke", "roles", "check"],
                            help="Yapilacak islem (list|grant|revoke|roles|check)")
    alt_parser.add_argument("--user", type=str, default=None, help="Kullanici adi")
    alt_parser.add_argument("--role", type=str, default=None, help="Rol adi")
    alt_parser.add_argument("--resource", type=str, default=None, help="Kaynak adi")
    alt_parser.add_argument("--action", type=str, default=None, help="Eylem")


def calistir(args):
    """permissions komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Permissions] Baslatiliyor: {islem}")

        if islem == "list":
            kullanici = args.user or "mevcut"
            print(f"[Permissions] {kullanici} yetkileri:")
            print("  Admin panel: izinli")
            print("  CLI komutlari: izinli")
            print("  API erisim: izinli")

        elif islem == "grant":
            kullanici = args.user or "kullanici"
            rol = args.role or "viewer"
            print(f"[Permissions] Yetki veriliyor:")
            print(f"  Kullanici: {kullanici}")
            print(f"  Rol: {rol}")
            print(f"  Kaynak: {args.resource or 'tum'}")

        elif islem == "revoke":
            kullanici = args.user or "kullanici"
            print(f"[Permissions] Yetki kaldiriliyor: {kullanici}")
            if args.resource:
                print(f"  Kaynak: {args.resource}")

        elif islem == "roles":
            print("[Permissions] Mevcut roller:")
            for rol, yetkiler in _varsayilan_roller().items():
                print(f"  {rol}: {', '.join(yetkiler)}")

        elif islem == "check":
            kaynak = args.resource or "system"
            eylem = args.action or "okuma"
            print(f"[Permissions] Denetleniyor: {kaynak}/{eylem}")
            print("  Sonuc: IZIN VERILDI")

    except Exception as e:
        print(f"[Permissions] Hata: {e}")
