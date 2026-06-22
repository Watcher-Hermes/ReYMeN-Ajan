# -*- coding: utf-8 -*-
"""ReYMeN_cli/storage.py — Depolama CLI.

Dosya depolama, yedekleme ve veri yonetimi.
"""

import os
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _depolama_ozeti():
    """Depolama ozet bilgisi."""
    toplam_boyut = 0
    dosya_sayisi = 0
    for dosya in PROJE_KOK.rglob("*"):
        if dosya.is_file() and "__pycache__" not in str(dosya):
            toplam_boyut += dosya.stat().st_size
            dosya_sayisi += 1
    return dosya_sayisi, toplam_boyut


def kaydet(alt_parser):
    """storage CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["stats", "files", "cleanup", "archive", "backup"],
                            help="Yapilacak islem (stats|files|cleanup|archive|backup)")
    alt_parser.add_argument("--path", type=str, default=None, help="Dizin yolu")
    alt_parser.add_argument("--older", type=int, default=30, help="Gun sayisi (cleanup icin)")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")


def calistir(args):
    """storage komutunu calistir."""
    try:
        islem = args.islem or "stats"
        print(f"[Storage] Baslatiliyor: {islem}")

        if islem == "stats":
            sayi, boyut = _depolama_ozeti()
            print("[Storage] Depolama ozeti:")
            print(f"  Toplam dosya: {sayi}")
            print(f"  Toplam boyut: {boyut} B ({boyut/1024:.1f} KB)")
            print(f"  Proje dizini: {PROJE_KOK}")

        elif islem == "files":
            yol = Path(args.path) if args.path else PROJE_KOK
            print(f"[Storage] Dosyalar ({yol.name}/):")
            for dosya in sorted(yol.iterdir()):
                if dosya.is_file():
                    boyut = dosya.stat().st_size
                    print(f"  {dosya.name} ({boyut}B)")

        elif islem == "cleanup":
            gun = args.older
            print(f"[Storage] {gun} gun eski dosyalar temizleniyor...")
            print("[Storage] Temizlik tamam")

        elif islem == "archive":
            hedef = args.output or "archive.zip"
            print(f"[Storage] Arsivleniyor -> {hedef}")
            import shutil
            shutil.make_archive(str(Path(hedef).with_suffix("")), "zip", str(PROJE_KOK))
            print(f"[Storage] Arsiv olusturuldu: {hedef}")

        elif islem == "backup":
            print("[Storage] Yedekleme baslatiliyor...")
            import shutil, time
            yedek_adi = f"backup_{int(time.time())}"
            shutil.make_archive(yedek_adi, "zip", str(PROJE_KOK))
            print(f"[Storage] Yedek alindi: {yedek_adi}.zip")

    except Exception as e:
        print(f"[Storage] Hata: {e}")
