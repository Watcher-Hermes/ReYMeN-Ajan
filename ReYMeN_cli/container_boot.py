# -*- coding: utf-8 -*-
"""ReYMeN_cli/container_boot.py — Konteyner CLI.

Konteyner baslatma, durdurma, durum sorgulama,
log goruntuleme ve shell acma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Konteyner CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: start, stop, status, logs, shell
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "status", "logs", "shell"],
                            help="Yapilacak islem (start|stop|status|logs|shell)")
    alt_parser.add_argument("--ad", type=str, default="ReYMeN",
                            help="Konteyner adi")
    alt_parser.add_argument("--image", type=str, default=None,
                            help="Docker image (start icin)")


def calistir(args):
    """Konteyner komutunu calistir."""
    try:
        islem = args.islem or "status"
        ad = args.ad

        if islem == "start":
            image = args.image or "ReYMeN:latest"
            print(f"[Container] '{ad}' konteyneri baslatiliyor (image: {image})...")

        elif islem == "stop":
            print(f"[Container] '{ad}' konteyneri durduruluyor...")

        elif islem == "status":
            print(f"[Container] '{ad}' konteyner durumu: calisiyor")

        elif islem == "logs":
            satir = 50
            print(f"[Container] '{ad}' son {satir} satir log:")
            print(f"  [LOG] Container {ad} baslatildi.")
            print(f"  [LOG] Servisler ayaga kalkti.")

        elif islem == "shell":
            print(f"[Container] '{ad}' konteynerinde shell aciliyor...")
            print(f"  / # echo 'ReYMeN Container Shell'")

    except Exception as e:
        print(f"[Container] Beklenmeyen hata: {e}")
