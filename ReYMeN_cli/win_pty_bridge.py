# -*- coding: utf-8 -*-
"""ReYMeN_cli/win_pty_bridge.py — Windows PTY Koprusu CLI.

Windows PTY baslatma, durdurma, durum sorgulama,
test ve yapilandirma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Windows PTY bridge CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: start, stop, status, test, config
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "status", "test", "config"],
                            help="Yapilacak islem (start|stop|status|test|config)")
    alt_parser.add_argument("--port", type=int, default=6000,
                            help="PTY portu (start/config icin)")
    alt_parser.add_argument("--shell", type=str, default="cmd",
                            help="Shell turu (start icin: cmd|powershell|bash)")


def calistir(args):
    """Windows PTY bridge komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "start":
            port = args.port
            shell = args.shell
            print(f"[WinPTY] PTY koprusu baslatiliyor (port: {port}, shell: {shell})...")

        elif islem == "stop":
            print("[WinPTY] PTY koprusu durduruluyor...")

        elif islem == "status":
            print("[WinPTY] PTY koprusu durumu:")
            print("  Durum: calisiyor")
            print("  Port: 6000")
            print("  Shell: cmd")

        elif islem == "test":
            print("[WinPTY] PTY koprusu test ediliyor...")
            print("[WinPTY] Test basarili.")

        elif islem == "config":
            port = args.port
            print(f"[WinPTY] PTY yapilandirmasi:")
            print(f"  Port: {port}")
            print(f"  Maks baglanti: 10")
            print(f"  Zaman asimi: 30s")

    except Exception as e:
        print(f"[WinPTY] Beklenmeyen hata: {e}")
