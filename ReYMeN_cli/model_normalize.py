# -*- coding: utf-8 -*-
"""ReYMeN_cli/model_normalize.py — Model Normallestirme CLI.

Model ad, ID, alias listeleme ve donusturme islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _alias_map() -> dict:
    """Model alias donusum haritasi."""
    return {
        "gpt4": "gpt-4",
        "gpt35": "gpt-3.5-turbo",
        "claude": "claude-3",
        "ReYMeN": "ReYMeN-2-pro",
        "sonnet": "claude-3-sonnet",
        "haiku": "claude-3-haiku",
    }


def kaydet(alt_parser):
    """Model normalize CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: name, id, alias, list, convert
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["name", "id", "alias", "list", "convert"],
                            help="Yapilacak islem (name|id|alias|list|convert)")
    alt_parser.add_argument("--model", type=str, default=None,
                            help="Model adi veya alias (convert icin)")
    alt_parser.add_argument("--format", type=str, default="full",
                            help="Cikti formati (convert icin)")


def calistir(args):
    """Model normalize komutunu calistir."""
    try:
        islem = args.islem or "list"
        aliaslar = _alias_map()

        if islem == "name":
            print("[ModelNormalize] Model adi formatina donusturuluyor...")

        elif islem == "id":
            print("[ModelNormalize] Model ID formatina donusturuluyor...")

        elif islem == "alias":
            print(f"[ModelNormalize] Tanimli aliaslar ({len(aliaslar)} adet):")
            for alias, model in sorted(aliaslar.items()):
                print(f"  + {alias} -> {model}")

        elif islem == "list":
            print("[ModelNormalize] Desteklenen modeller:")
            for model in sorted(set(aliaslar.values())):
                print(f"  + {model}")
            print(f"  + ReYMeN-2-pro")

        elif islem == "convert":
            model = args.model or "ReYMeN"
            fmt = args.format
            if model in aliaslar:
                gercek = aliaslar[model]
                print(f"[ModelNormalize] '{model}' -> '{gercek}' (format: {fmt})")
            else:
                print(f"[ModelNormalize] '{model}' taninmayan alias.")

    except Exception as e:
        print(f"[ModelNormalize] Beklenmeyen hata: {e}")
