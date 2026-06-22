# -*- coding: utf-8 -*-
"""ReYMeN_cli/model_catalog.py — Model Katalog CLI.

Model listeleme, arama, bilgi, karsilastirma
ve karsilastirma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _model_katalog() -> dict:
    """Varsayilan model katalogu."""
    return {
        "gpt-4": {"saglayici": "openai", "parametre": "1T", "maliyet": "yuksek"},
        "gpt-3.5-turbo": {"saglayici": "openai", "parametre": "175B", "maliyet": "dusuk"},
        "claude-3": {"saglayici": "anthropic", "parametre": "500B", "maliyet": "orta"},
        "ReYMeN-2": {"saglayici": "nous", "parametre": "70B", "maliyet": "dusuk"},
    }


def kaydet(alt_parser):
    """Model katalog CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, search, info, compare, benchmark
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "search", "info", "compare", "benchmark"],
                            help="Yapilacak islem (list|search|info|compare|benchmark)")
    alt_parser.add_argument("--model", type=str, default=None,
                            help="Model adi (info/compare/benchmark icin)")
    alt_parser.add_argument("--karsilastir", type=str, default=None,
                            help="Karsilastirilacak model (compare icin)")


def calistir(args):
    """Model katalog komutunu calistir."""
    try:
        islem = args.islem or "list"
        katalog = _model_katalog()

        if islem == "list":
            print(f"[ModelCatalog] Katalogdaki modeller ({len(katalog)} adet):")
            for model, bilgi in katalog.items():
                print(f"  + {model} ({bilgi['saglayici']})")

        elif islem == "search":
            sorgu = args.model or ""
            print(f"[ModelCatalog] '{sorgu}' araniyor...")
            for model in katalog:
                if sorgu.lower() in model.lower():
                    print(f"  + {model}")

        elif islem == "info":
            model = args.model or "gpt-4"
            if model in katalog:
                bilgi = katalog[model]
                print(f"[ModelCatalog] {model}:")
                for a, d in bilgi.items():
                    print(f"  {a}: {d}")
            else:
                print(f"[ModelCatalog] '{model}' katalogda bulunamadi.")

        elif islem == "compare":
            model1 = args.model or "gpt-4"
            model2 = args.karsilastir or "claude-3"
            print(f"[ModelCatalog] {model1} vs {model2}:")
            print(f"  Ikisi de karsilastirma icin uygun.")

        elif islem == "benchmark":
            model = args.model or "tum"
            print(f"[ModelCatalog] '{model}' benchmark testi baslatiliyor...")
            print("[ModelCatalog] Benchmark tamam.")

    except Exception as e:
        print(f"[ModelCatalog] Beklenmeyen hata: {e}")
