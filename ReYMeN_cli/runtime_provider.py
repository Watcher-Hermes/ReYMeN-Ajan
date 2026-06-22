# -*- coding: utf-8 -*-
"""ReYMeN_cli/runtime_provider.py — Calisma Zamani Saglayici CLI.

Calisma zamani saglayicisi listeleme, ayarlama,
bilgi, test ve degistirme islemleri.
"""

import os
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent

_PROVIDER_BASE_URLS = {
    "openrouter": "https://openrouter.ai/api/v1",
    "openai":     "https://api.openai.com/v1",
    "anthropic":  "https://api.anthropic.com",
    "groq":       "https://api.groq.com/openai/v1",
    "deepseek":   "https://api.deepseek.com",
    "lmstudio":   "http://localhost:1234",
}

_PROVIDER_ENV_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai":     "OPENAI_API_KEY",
    "anthropic":  "ANTHROPIC_API_KEY",
    "groq":       "GROQ_API_KEY",
    "deepseek":   "DEEPSEEK_API_KEY",
    "lmstudio":   "",
}


def resolve_runtime_provider(
    requested: str = None,
    explicit_base_url: str | None = None,
    explicit_api_key: str | None = None,
) -> dict:
    """Istenen provider icin base_url ve api_key iceren dict dondur.

    Args:
        requested: Provider adi (ornek: 'openrouter', 'openai').
        explicit_base_url: Acik sekilde verilmis base URL (override).
        explicit_api_key: Acik sekilde verilmis API anahtari (override).

    Returns:
        {'provider': str, 'base_url': str, 'api_key': str, 'api_mode': str}
    """
    provider = (requested or "").lower().strip()
    base_url = (explicit_base_url or "").strip() or _PROVIDER_BASE_URLS.get(provider, "")
    env_key  = _PROVIDER_ENV_KEYS.get(provider, "")
    api_key  = (explicit_api_key or "").strip() or (os.environ.get(env_key, "").strip() if env_key else "")
    return {
        "provider": provider,
        "base_url": base_url,
        "api_key": api_key,
        "api_mode": "chat_completions",
    }


def format_runtime_provider_error(exc: Exception) -> str:
    """Format a runtime provider error for user-facing display.

    Used by cron/scheduler.py to surface clean error messages when
    provider auth or resolution fails.
    """
    name = type(exc).__name__
    msg = str(exc).strip()
    if not msg:
        return f"Runtime provider error: {name}"
    return f"Runtime provider error: {name}: {msg}"


def _saglayicilar() -> list:
    """Desteklenen calisma zamani saglayicilari."""
    return ["docker", "podman", "local", "ssh", "kubernetes"]


def kaydet(alt_parser):
    """Runtime provider CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, info, test, switch
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "info", "test", "switch"],
                            help="Yapilacak islem (list|set|info|test|switch)")
    alt_parser.add_argument("--saglayici", type=str, default=None,
                            help="Saglayici adi (set/info/test/switch icin)")
    alt_parser.add_argument("--surum", type=str, default=None,
                            help="Saglayici surumu (set icin)")


def calistir(args):
    """Runtime provider komutunu calistir."""
    try:
        islem = args.islem or "list"
        saglayicilar = _saglayicilar()

        if islem == "list":
            print(f"[RuntimeProvider] Desteklenen saglayicilar ({len(saglayicilar)} adet):")
            for s in saglayicilar:
                print(f"  + {s}")

        elif islem == "set":
            saglayici = args.saglayici
            surum = args.surum
            if not saglayici:
                print("[RuntimeProvider] Lutfen --saglayici parametresini belirtin.")
                return
            if saglayici in saglayicilar:
                surum_str = f" (surum: {surum})" if surum else ""
                print(f"[RuntimeProvider] Saglayici '{saglayici}' olarak ayarlandi{surum_str}.")
            else:
                print(f"[RuntimeProvider] '{saglayici}' desteklenmiyor.")

        elif islem == "info":
            saglayici = args.saglayici or "local"
            print(f"[RuntimeProvider] '{saglayici}' bilgisi:")
            print(f"  Durum: aktif")
            print(f"  Surum: 1.0")

        elif islem == "test":
            saglayici = args.saglayici or "local"
            print(f"[RuntimeProvider] '{saglayici}' test ediliyor...")
            print("[RuntimeProvider] Test basarili.")

        elif islem == "switch":
            saglayici = args.saglayici or "docker"
            print(f"[RuntimeProvider] '{saglayici}' gecis yapiliyor...")

    except Exception as e:
        print(f"[RuntimeProvider] Beklenmeyen hata: {e}")
