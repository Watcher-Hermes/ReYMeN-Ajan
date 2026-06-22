# -*- coding: utf-8 -*-
"""ReYMeN_cli/benchmarks.py — Performans Test CLI.

Sistem performans olcumleri, karsilastirmalar ve raporlama.
"""

import time
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _zamanla(fonk, *args, **kwargs):
    """Bir fonksiyonun calisma suresini olcer."""
    basla = time.perf_counter()
    sonuc = fonk(*args, **kwargs)
    gecen = time.perf_counter() - basla
    return sonuc, gecen


def _hiz_testi():
    """Basit Python hiz testleri."""
    sonuclar = {}
    # String birlestirme
    _, sure = _zamanla(lambda: "".join(str(i) for i in range(10000)))
    sonuclar["string_join_10k"] = round(sure, 4)
    # Liste olusturma
    _, sure = _zamanla(lambda: [i * 2 for i in range(100000)])
    sonuclar["list_comp_100k"] = round(sure, 4)
    # Sozluk erisim
    d = {i: i for i in range(10000)}
    _, sure = _zamanla(lambda: [d[i] for i in range(10000)])
    sonuclar["dict_access_10k"] = round(sure, 4)
    return sonuclar


def kaydet(alt_parser):
    """benchmarks CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["run", "cpu", "io", "list", "report"],
                            help="Yapilacak islem (run|cpu|io|list|report)")
    alt_parser.add_argument("--iterations", type=int, default=1, help="Test tekrari")
    alt_parser.add_argument("--output", type=str, default=None, help="Rapor dosyasi")


def calistir(args):
    """benchmarks komutunu calistir."""
    try:
        islem = args.islem or "run"
        print(f"[Benchmarks] Calistiriliyor: {islem}")

        if islem == "run":
            for i in range(args.iterations):
                print(f"\n--- Test # {i + 1} ---")
                sonuclar = _hiz_testi()
                for test, sure in sonuclar.items():
                    print(f"  {test}: {sure}s")

        elif islem == "cpu":
            import math
            basla = time.perf_counter()
            _ = [math.sqrt(i) for i in range(1000000)]
            sure = round(time.perf_counter() - basla, 4)
            print(f"[Benchmarks] CPU test: 1M sqrt = {sure}s")

        elif islem == "io":
            import tempfile
            import os
            basla = time.perf_counter()
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * 1024 * 1024)
                tmp_ad = f.name
            with open(tmp_ad, "rb") as f:
                _ = f.read()
            os.unlink(tmp_ad)
            sure = round(time.perf_counter() - basla, 4)
            print(f"[Benchmarks] IO test: 1MB yaz/oku = {sure}s")

        elif islem == "list":
            print("[Benchmarks] Mevcut testler: run, cpu, io")
            print("[Benchmarks] Rapor: --output ile kaydedin")

        elif islem == "report":
            sonuclar = _hiz_testi()
            if args.output:
                import json
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(sonuclar, f, indent=2)
                print(f"[Benchmarks] Rapor kaydedildi: {args.output}")
            else:
                print("[Benchmarks] Lutfen --output belirtin")

    except Exception as e:
        print(f"[Benchmarks] Hata: {e}")
