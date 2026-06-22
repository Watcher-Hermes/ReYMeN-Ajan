# -*- coding: utf-8 -*-
"""ReYMeN_cli/send_cmd.py — Komut Gonder CLI.

Metin, dosya, URL, API ve yayin gibi komutlari
gonderme islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Send command CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: text, file, url, api, broadcast
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["text", "file", "url", "api", "broadcast"],
                            help="Yapilacak islem (text|file|url|api|broadcast)")
    alt_parser.add_argument("--icerik", type=str, default=None,
                            help="Gonderilecek icerik (text/api/broadcast icin)")
    alt_parser.add_argument("--hedef", type=str, default=None,
                            help="Hedef URL veya dosya (file/url/api icin)")
    alt_parser.add_argument("--kanal", type=str, default="general",
                            help="Yayin kanali (broadcast icin)")


def calistir(args):
    """Send command komutunu calistir."""
    try:
        islem = args.islem or "text"

        if islem == "text":
            icerik = args.icerik or "Merhaba, ReYMeN CLI!"
            print(f"[SendCmd] Metin gonderiliyor: '{icerik}'")

        elif islem == "file":
            hedef = args.hedef or "README.md"
            print(f"[SendCmd] Dosya gonderiliyor: '{hedef}'")

        elif islem == "url":
            hedef = args.hedef or "http://localhost:8080/api"
            icerik = args.icerik or "GET"
            print(f"[SendCmd] URL'ye istek: {icerik} {hedef}")

        elif islem == "api":
            hedef = args.hedef or "http://localhost:8080/api/v1"
            icerik = args.icerik or '{"key": "value"}'
            print(f"[SendCmd] API cagrisi: POST {hedef}")
            print(f"[SendCmd] Veri: {icerik}")

        elif islem == "broadcast":
            icerik = args.icerik or "Duyuru"
            kanal = args.kanal
            print(f"[SendCmd] '{kanal}' kanalinda yayin: '{icerik}'")

    except Exception as e:
        print(f"[SendCmd] Beklenmeyen hata: {e}")
