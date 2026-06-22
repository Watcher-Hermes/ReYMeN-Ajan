# -*- coding: utf-8 -*-
"""ReYMeN_cli/search_cli.py — Arama CLI.

Dosya, metin, modul ve yapilandirma arama islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _dosya_ara(sorgu: str) -> list[Path]:
    """Dosya adinda arama yapar."""
    sonuc = []
    for dosya in PROJE_KOK.rglob(f"*{sorgu}*"):
        if dosya.is_file() and "__pycache__" not in str(dosya):
            sonuc.append(dosya)
    return sonuc[:20]


def kaydet(alt_parser):
    """search_cli CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["files", "text", "modules", "config", "help"],
                            help="Yapilacak islem (files|text|modules|config|help)")
    alt_parser.add_argument("--query", type=str, default=None, help="Arama sorgusu")
    alt_parser.add_argument("--type", type=str, default=None, help="Dosya turu (.py, .json)")
    alt_parser.add_argument("--max", type=int, default=10, help="Maksimum sonuc")


def calistir(args):
    """search_cli komutunu calistir."""
    try:
        islem = args.islem or "files"
        sorgu = args.query or "*.py"
        print(f"[Search] Baslatiliyor: {islem}")

        if islem == "files":
            print(f"[Search] Dosya araniyor: {sorgu}")
            sonuclar = _dosya_ara(sorgu)
            if sonuclar:
                for dosya in sonuclar[:args.max]:
                    print(f"  + {dosya.relative_to(PROJE_KOK)}")
                print(f"  Toplam: {len(sonuclar)} sonuc")
            else:
                print("  Sonuc bulunamadi")

        elif islem == "text":
            print(f"[Search] Metin araniyor: {sorgu}")
            import subprocess
            try:
                sonuc = subprocess.run(
                    ["grep", "-r", "-l", sorgu, str(PROJE_KOK / "ReYMeN_cli")],
                    capture_output=True, text=True, timeout=5
                )
                satirlar = [s for s in sonuc.stdout.strip().split("\n") if s]
                for s in satirlar[:args.max]:
                    print(f"  + {Path(s).name}")
                print(f"  Toplam: {len(satirlar)} sonuc")
            except Exception:
                print("  Arama yapilamadi")

        elif islem == "modules":
            print("[Search] Modul arama:")
            import pkg_resources
            for m in sorted(pkg_resources.working_set):
                if sorgu.lower() in m.project_name.lower():
                    print(f"  + {m.project_name}=={m.version}")

        elif islem == "config":
            print(f"[Search] Yapilandirma araniyor: {sorgu}")
            for dosya in PROJE_KOK.rglob("*.json"):
                if "__pycache__" not in str(dosya):
                    print(f"  + {dosya.relative_to(PROJE_KOK)}")

        elif islem == "help":
            print("[Search] Kullanim:")
            print("  search_cli files --query=ornek")
            print("  search_cli text --query=fonksiyon")
            print("  search_cli modules --query=flask")

    except Exception as e:
        print(f"[Search] Hata: {e}")
