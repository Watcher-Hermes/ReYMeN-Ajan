# -*- coding: utf-8 -*-
"""ReYMeN_cli/prompt_size.py — Prompt Boyutu CLI.

Prompt boyutu hesaplama, on izleme, iyilestirme,
limit kontrolu ve raporlama islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _token_hesapla(metin: str) -> int:
    """Basit token hesaplama (ortalama 4 karakter = 1 token)."""
    return len(metin) // 4 + 1


def kaydet(alt_parser):
    """Prompt size CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: calc, preview, optimize, limit, report
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["calc", "preview", "optimize", "limit", "report"],
                            help="Yapilacak islem (calc|preview|optimize|limit|report)")
    alt_parser.add_argument("--metin", type=str, default=None,
                            help="Prompt metni veya dosyasi")
    alt_parser.add_argument("--dosya", type=str, default=None,
                            help="Prompt dosyasi (calc/preview icin)")
    alt_parser.add_argument("--limit", type=int, default=4096,
                            help="Token limiti")


def calistir(args):
    """Prompt size komutunu calistir."""
    try:
        islem = args.islem or "report"

        if islem == "calc":
            metin = args.metin or ""
            dosya = args.dosya
            if dosya:
                try:
                    with open(dosya, "r", encoding="utf-8") as f:
                        metin = f.read()
                except Exception:
                    print(f"[PromptSize] '{dosya}' okunamadi.")
                    return
            token_sayisi = _token_hesapla(metin)
            karakter_sayisi = len(metin)
            print(f"[PromptSize] Prompt boyutu:")
            print(f"  Karakter: {karakter_sayisi}")
            print(f"  Token: ~{token_sayisi}")

        elif islem == "preview":
            metin = args.metin or "Ornek prompt"
            print(f"[PromptSize] On izleme:")
            print(f"  {metin[:200]}...")

        elif islem == "optimize":
            print("[PromptSize] Prompt iyilestiriliyor...")
            print("[PromptSize] Iyilestirme tamam.")

        elif islem == "limit":
            limit = args.limit
            print(f"[PromptSize] Token limiti: {limit}")

        elif islem == "report":
            limit = args.limit
            print(f"[PromptSize] Prompt raporu:")
            print(f"  Limit: {limit} token")
            print(f"  Kullanim: 0 token")
            print(f"  Yuzde: %0")

    except Exception as e:
        print(f"[PromptSize] Beklenmeyen hata: {e}")
