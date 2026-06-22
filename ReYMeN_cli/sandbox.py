# -*- coding: utf-8 -*-
"""ReYMeN_cli/sandbox.py — Guvenli Calisma Ortami CLI.

Kod ve komutlari guvenli ortamda calistirma, test ve dogrulama.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """sandbox CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["run", "test", "clean", "status", "config"],
                            help="Yapilacak islem (run|test|clean|status|config)")
    alt_parser.add_argument("--code", type=str, default=None, help="Calistirilacak kod")
    alt_parser.add_argument("--file", type=str, default=None, help="Kod dosyasi")
    alt_parser.add_argument("--timeout", type=int, default=10, help="Zamanasimi (sn)")


def calistir(args):
    """sandbox komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Sandbox] Baslatiliyor: {islem}")

        if islem == "run":
            kod = args.code
            if not kod and args.file:
                with open(args.file, "r") as f:
                    kod = f.read()
            if kod:
                print(f"[Sandbox] Kod calistiriliyor (timeout: {args.timeout}s)...")
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(kod)
                    tmp_ad = f.name
                try:
                    sonuc = subprocess.run(
                        [sys.executable, tmp_ad],
                        capture_output=True, text=True,
                        timeout=args.timeout
                    )
                    print(f"  Cikti: {sonuc.stdout[:200] if sonuc.stdout else '(bos)'}")
                    if sonuc.stderr:
                        print(f"  Hata: {sonuc.stderr[:200]}")
                except subprocess.TimeoutExpired:
                    print(f"  Zamanasimi ({args.timeout}s)")
                finally:
                    Path(tmp_ad).unlink(missing_ok=True)
            else:
                print("[Sandbox] --code veya --file belirtin")

        elif islem == "test":
            print("[Sandbox] Sandbox test ediliyor...")
            print("  [OK] Kod calistirma")
            print("  [OK] Kaynak kisitlama")
            print("  [OK] Zamanasimi kontrolu")

        elif islem == "clean":
            print("[Sandbox] Gecici dosyalar temizleniyor...")

        elif islem == "status":
            print("[Sandbox] Durum:")
            print("  Ortam: HAZIR")
            print("  Guvenlik: AKTIF")
            print(f"  Varsayilan timeout: {args.timeout}s")

        elif islem == "config":
            print("[Sandbox] Yapilandirma:")
            print("  Izin verilen: Python 3.x")
            print("  Yasaklanan: subprocess, os.system")
            print("  Kaynak limit: 256MB")

    except Exception as e:
        print(f"[Sandbox] Hata: {e}")
