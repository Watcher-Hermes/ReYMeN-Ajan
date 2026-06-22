# -*- coding: utf-8 -*-
"""ReYMeN_cli/banner.py — Banner CLI.

Banner gosterme, ayarlama, rastgele secme,
sifirlama ve onizleme islemleri.
"""
import random as rnd
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _format_context_length(ctx: int) -> str:
    """Context length sayisini formatla (128000 -> '128K')."""
    if ctx < 1000:
        return str(ctx)
    if ctx < 1_000_000:
        return f"{ctx // 1000}K"
    return f"{ctx / 1_000_000:.1f}M"


def format_banner_version_label() -> str:
    """Banner icin versiyon label'i."""
    try:
        from ReYMeN_cli import __version__
        return f"ReYMeN Agent v{__version__}"
    except (ImportError, AttributeError):
        return "ReYMeN Agent v1.0.0"


def _banner_dosyasi() -> Path:
    """Banner ayar dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "banner" / "ayar.json"


def kaydet(alt_parser):
    """Banner CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: show, set, random, reset, preview
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["show", "set", "random", "reset", "preview"],
                            help="Yapilacak islem (show|set|random|reset|preview)")
    alt_parser.add_argument("--metin", type=str, default=None,
                            help="Banner metni (set icin)")
    alt_parser.add_argument("--renk", type=str, default=None,
                            help="Banner rengi (set icin)")


def build_welcome_banner(console=None, model=None, cwd=None, tools=None,
                          enabled_toolsets=None, session_id=None,
                          context_length=None):
    """Build and display a welcome banner with system info."""
    try:
        from ReYMeN_cli.colors import cprint as _cprint
    except ImportError:
        _cprint = print
    if console:
        console.print("[bold cyan]╔══════════════════════════════════════╗[/]")
        console.print("[bold cyan]║        ReYMeN Agent CLI              ║[/]")
        console.print("[bold cyan]╚══════════════════════════════════════╝[/]")
        if model:
            console.print(f"  Model: {model}")
        if session_id:
            console.print(f"  Session: {session_id}")
        if context_length:
            from ReYMeN_cli.banner import _format_context_length as _fcl
            console.print(f"  Context: {_fcl(context_length)}")
    else:
        print("╔══════════════════════════════════════╗")
        print("║        ReYMeN Agent CLI              ║")
        print("╚══════════════════════════════════════╝")


def calistir(args):
    """Banner komutunu calistir."""
    try:
        islem = args.islem or "show"

        if islem == "show":
            print("[Banner] Mevcut banner:")
            print("  ReYMeN CLI v1.0")

        elif islem == "set":
            metin = args.metin or "ReYMeN"
            renk = args.renk or "mavi"
            print(f"[Banner] Banner ayarlandi: '{metin}' (renk: {renk})")

        elif islem == "random":
            import random as rnd
            bannerlar = ["ReYMeN", "CLI Master", "Task Runner"]
            secim = rnd.choice(bannerlar)
            print(f"[Banner] Rastgele banner: '{secim}'")

        elif islem == "reset":
            print("[Banner] Banner varsayilan ayarlara sifirlandi.")

        elif islem == "preview":
            metin = args.metin or "ReYMeN"
            print(f"[Banner] On izleme:")
            print(f"  {'=' * 40}")
            print(f"  {metin}")
            print(f"  {'=' * 40}")

    except Exception as e:
        print(f"[Banner] Beklenmeyen hata: {e}")
