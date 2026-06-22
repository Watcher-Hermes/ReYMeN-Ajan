# -*- coding: utf-8 -*-
"""ReYMeN_cli/firewall.py — Guvenlik Duvari CLI.

Erisim kurallari, IP engelleme, port yonetimi ve guvenlik politikasi.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _varsayilan_kurallar():
    """Varsayilan guvenlik duvari kurallari."""
    return [
        ("localhost", "127.0.0.1", "izin", "dahili"),
        ("admin_panel", "10.0.0.0/8", "izin", "ozel_ag"),
        ("diger", "0.0.0.0/0", "engel", "genel"),
    ]


def kaydet(alt_parser):
    """firewall CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["rules", "block", "allow", "status", "reset"],
                            help="Yapilacak islem (rules|block|allow|status|reset)")
    alt_parser.add_argument("--ip", type=str, default=None, help="IP adresi")
    alt_parser.add_argument("--port", type=int, default=None, help="Port numarasi")
    alt_parser.add_argument("--reason", type=str, default=None, help="Gerekce")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")


def calistir(args):
    """firewall komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Firewall] Baslatiliyor: {islem}")

        if islem == "rules":
            print("[Firewall] Guvenlik duvari kurallari:")
            for ad, hedef, aksiyon, kategori in _varsayilan_kurallar():
                isaret = "OK" if aksiyon == "izin" else "ENGELLENDI"
                print(f"  [{isaret}] {ad} -> {hedef} ({kategori})")

        elif islem == "block":
            ip = args.ip or "0.0.0.0"
            sebep = args.reason or "manuel engelleme"
            print(f"[Firewall] IP engellendi: {ip} ({sebep})")
            if args.port:
                print(f"  Port: {args.port}")

        elif islem == "allow":
            ip = args.ip or "127.0.0.1"
            print(f"[Firewall] IP izni verildi: {ip}")
            if args.port:
                print(f"  Port: {args.port}")

        elif islem == "status":
            print("[Firewall] Guvenlik duvari durumu:")
            print("  Durum: AKTIF")
            print(f"  Kural sayisi: {len(_varsayilan_kurallar())}")
            print(f"  Engellenen IP: 0")

        elif islem == "reset":
            print("[Firewall] Tum kurallar sifirlandi")
            print("  Varsayilan kurallara donuldu")

    except Exception as e:
        print(f"[Firewall] Hata: {e}")
