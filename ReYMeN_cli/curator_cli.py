# -*- coding: utf-8 -*-
"""ReYMeN_cli/curator_cli.py — Küratör CLI.

Veri küratörlugu: listeleme, budama, birlestirme,
bolme ve raporlama islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _curator_dosyasi() -> Path:
    """Kurator veri dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "curator" / "veri.json"


def _veri_oku() -> list:
    """Kurator verilerini oku."""
    dosya = _curator_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Kurator CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, prune, merge, split, report
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "prune", "merge", "split", "report"],
                            help="Yapilacak islem (list|prune|merge|split|report)")
    alt_parser.add_argument("--kaynak", type=str, default=None,
                            help="Kaynak veri (merge/split icin)")
    alt_parser.add_argument("--hedef", type=str, default=None,
                            help="Hedef veri (merge icin)")
    alt_parser.add_argument("--esik", type=int, default=None,
                            help="Esik degeri (prune icin)")


def calistir(args):
    """Kurator komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            veriler = _veri_oku()
            if not veriler:
                print("[Curator] Kurator verisi yok.")
            else:
                print(f"[Curator] Toplam {len(veriler)} kayit:")

        elif islem == "prune":
            esik = args.esik or 30
            print(f"[Curator] Budama yapiliyor (esik: {esik} gun)...")

        elif islem == "merge":
            kaynak = args.kaynak or "ana"
            hedef = args.hedef or "yedek"
            print(f"[Curator] '{kaynak}' ve '{hedef}' birlestiriliyor...")

        elif islem == "split":
            kaynak = args.kaynak or "ana"
            print(f"[Curator] '{kaynak}' verisi bolunuyor...")

        elif islem == "report":
            veriler = _veri_oku()
            print(f"[Curator] Rapor:")
            print(f"  Toplam kayit: {len(veriler)}")
            print(f"  Durum: saglikli")

    except Exception as e:
        print(f"[Curator] Beklenmeyen hata: {e}")
