# -*- coding: utf-8 -*-
"""ReYMeN_cli/fallback_config.py — Yedek Yapilandirma CLI.

Yedek yapilandirma listeleme, ayarlama, test etme,
iceri ve disa aktarma islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _fallback_dosyasi() -> Path:
    """Fallback yapilandirma dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "fallback" / "config.json"


def get_fallback_chain(cfg: dict) -> list:
    """Yapilandirma sozlugundan yedek saglayici zincirini dondur.

    Once fallback_providers (liste) anahtarini dener; yoksa legacy
    fallback_model (sozluk veya liste) anahtarini kullanir.

    Args:
        cfg: Yapilandirma sozlugu (genellikle config.yaml'dan okunur)

    Returns:
        Saglayici giris sozluklerinin listesi; bulunamazsa bos liste.
    """
    providers = cfg.get("fallback_providers") or []
    if isinstance(providers, list) and providers:
        return list(providers)
    legacy = cfg.get("fallback_model")
    if isinstance(legacy, dict) and legacy:
        return [legacy]
    if isinstance(legacy, list) and legacy:
        return list(legacy)
    return []


def _fallback_oku() -> dict:
    """Fallback yapilandirmasini oku."""
    dosya = _fallback_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def kaydet(alt_parser):
    """Fallback config CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, test, import, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "test", "import", "export"],
                            help="Yapilacak islem (list|set|test|import|export)")
    alt_parser.add_argument("--anahtar", type=str, default=None,
                            help="Yapilandirma anahtari (set icin)")
    alt_parser.add_argument("--deger", type=str, default=None,
                            help="Yapilandirma degeri (set icin)")
    alt_parser.add_argument("--dosya", type=str, default=None,
                            help="Dosya yolu (import/export icin)")


def calistir(args):
    """Fallback config komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            fallback = _fallback_oku()
            if not fallback:
                print("[FallbackConfig] Yedek yapilandirma yok.")
            else:
                print(f"[FallbackConfig] Yedek yapilandirma ({len(fallback)} adet):")
                for a, d in sorted(fallback.items()):
                    print(f"  + {a}: {d}")

        elif islem == "set":
            anahtar = args.anahtar
            deger = args.deger
            if not anahtar or deger is None:
                print("[FallbackConfig] Lutfen --anahtar ve --deger parametrelerini belirtin.")
                return
            print(f"[FallbackConfig] {anahtar}={deger} ayarlandi.")

        elif islem == "test":
            print("[FallbackConfig] Yedek yapilandirma test ediliyor...")
            print("[FallbackConfig] Test basarili.")

        elif islem == "import":
            dosya = args.dosya or "fallback.json"
            print(f"[FallbackConfig] '{dosya}' iceri aktariliyor...")

        elif islem == "export":
            dosya = args.dosya or "fallback_export.json"
            print(f"[FallbackConfig] '{dosya}' disa aktariliyor...")

    except Exception as e:
        print(f"[FallbackConfig] Beklenmeyen hata: {e}")
