# -*- coding: utf-8 -*-
"""ReYMeN_cli/template.py — Sablon CLI.

Dosya ve proje sablonlarini yonetme, olusturma ve uygulama.
"""

from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
SABLON_DIZIN = PROJE_KOK / "templates"


def _sablon_listesi():
    """Mevcut sablonlari listeler."""
    sablonlar = []
    if SABLON_DIZIN.exists():
        for dosya in SABLON_DIZIN.glob("*.py"):
            sablonlar.append(dosya.stem)
    if not sablonlar:
        sablonlar = ["cli_modul", "gateway_eklenti", "plugin"]
    return sablonlar


def kaydet(alt_parser):
    """template CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "create", "apply", "edit", "remove"],
                            help="Yapilacak islem (list|create|apply|edit|remove)")
    alt_parser.add_argument("--name", type=str, default=None, help="Sablon adi")
    alt_parser.add_argument("--output", type=str, default=None, help="Olusturulacak dosya")
    alt_parser.add_argument("--type", type=str, default=None, help="Sablon turu")


def calistir(args):
    """template komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Template] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Template] Mevcut sablonlar:")
            for sablon in _sablon_listesi():
                print(f"  + {sablon}")

        elif islem == "create":
            ad = args.name or "yeni_sablon"
            tur = args.type or "cli_modul"
            SABLON_DIZIN.mkdir(parents=True, exist_ok=True)
            sablon_icerik = f"""# -*- coding: utf-8 -*-
\"\"\"{ad}.py — {tur} sablonu.\"\"\"

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["default"], help="Yapilacak islem")


def calistir(args):
    try:
        print(f"[{ad}] Calistiriliyor...")
    except Exception as e:
        print(f"[{ad}] Hata: {{e}}")
"""
            with open(str(SABLON_DIZIN / f"{ad}.py"), "w", encoding="utf-8") as f:
                f.write(sablon_icerik)
            print(f"[Template] Sablon olusturuldu: {ad} ({tur})")

        elif islem == "apply":
            ad = args.name or "cli_modul"
            cikti = args.output or "yeni_modul.py"
            print(f"[Template] Uygulaniyor: {ad} -> {cikti}")
            # Sablonu hedefe kopyala
            kaynak = SABLON_DIZIN / f"{ad}.py"
            hedef = PROJE_KOK / cikti
            if kaynak.exists():
                hedef.write_text(kaynak.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"  Olusturuldu: {hedef}")
            else:
                print(f"  Sablon bulunamadi: {ad}")

        elif islem == "edit":
            ad = args.name
            if ad:
                sablon_yolu = SABLON_DIZIN / f"{ad}.py"
                if sablon_yolu.exists():
                    print(f"[Template] Sablon icerigi ({ad}):")
                    print(sablon_yolu.read_text(encoding="utf-8")[:200])
                else:
                    print(f"  Sablon bulunamadi: {ad}")
            else:
                print("[Template] --name belirtin")

        elif islem == "remove":
            ad = args.name
            if ad:
                sablon_yolu = SABLON_DIZIN / f"{ad}.py"
                if sablon_yolu.exists():
                    sablon_yolu.unlink()
                    print(f"[Template] Sablon silindi: {ad}")
                else:
                    print(f"  Sablon bulunamadi: {ad}")
            else:
                print("[Template] --name belirtin")

    except Exception as e:
        print(f"[Template] Hata: {e}")
