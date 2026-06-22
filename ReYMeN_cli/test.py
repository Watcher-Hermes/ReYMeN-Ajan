# -*- coding: utf-8 -*-
"""ReYMeN_cli/test.py — Test CLI.

Test calistirma, listeleme, kod kapsami, izleme ve raporlama.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _test_dosyalari() -> list:
    """Projedeki test dosyalarini bul."""
    kalip = ["test_*.py", "*_test.py", "tests/*.py"]
    sonuc = []
    for k in kalip:
        for f in PROJE_KOK.glob(k):
            sonuc.append(f)
        for f in (PROJE_KOK / "tests").glob(k.split("/")[-1]) if (PROJE_KOK / "tests").exists() else []:
            if f not in sonuc:
                sonuc.append(f)
    return sorted(set(sonuc))


def kaydet(alt_parser):
    """Test CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: run, list, coverage, watch, report
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["run", "list", "coverage", "watch", "report"],
                            help="Yapilacak islem (run|list|coverage|watch|report)")
    alt_parser.add_argument("--test", type=str, default=None,
                            help="Belirli bir test dosyasi")
    alt_parser.add_argument("--verbose", "-v", action="store_true",
                            help="Ayrintili cikti")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Rapor cikti dosyasi")


def calistir(args):
    """Test komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            testler = _test_dosyalari()
            if not testler:
                print("[Test] Projede test dosyasi bulunamadi.")
                return
            print(f"[Test] Test dosyalari ({len(testler)} adet):")
            for t in testler:
                try:
                    with open(str(t), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    test_sayisi = icerik.count("def test_")
                    print(f"  + {t.relative_to(PROJE_KOK)} ({test_sayisi} test)")
                except Exception:
                    print(f"  + {t.relative_to(PROJE_KOK)}")

        elif islem == "run":
            test_hedef = args.test
            verbose = args.verbose
            print(f"[Test] Testler calistiriliyor...")
            cmd = [sys.executable, "-m", "pytest"]
            if verbose:
                cmd.append("-v")
            if test_hedef:
                cmd.append(test_hedef)
            else:
                cmd.append(str(PROJE_KOK))
            cmd.extend(["-x", "--tb=short"])
            try:
                result = subprocess.run(cmd, cwd=str(PROJE_KOK), capture_output=True, text=True)
                print(result.stdout)
                if result.returncode == 0:
                    print("[Test] Tum testler gecti.")
                else:
                    print("[Test] Bazi testler basarisiz oldu.")
                    if result.stderr:
                        print(result.stderr)
            except FileNotFoundError:
                print("[Test] pytest yuklu degil. pip install pytest")

        elif islem == "coverage":
            print("[Test] Kod kapsami olculuyor...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "coverage", "run", "-m", "pytest"],
                    cwd=str(PROJE_KOK), capture_output=True, text=True
                )
                result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report"],
                    cwd=str(PROJE_KOK), capture_output=True, text=True
                )
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except FileNotFoundError:
                print("[Test] coverage yuklu degil. pip install coverage pytest")

        elif islem == "watch":
            print("[Test] Test izleme baslatildi... (Cikmak icin Ctrl+C)")
            try:
                import time
                while True:
                    os.system("cls" if sys.platform == "win32" else "clear")
                    print(f"[Test] Izleniyor... ({datetime.now().strftime('%H:%M:%S')})")
                    print()
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", "--tb=short", "-q"],
                        cwd=str(PROJE_KOK), capture_output=True, text=True
                    )
                    print(result.stdout)
                    if result.returncode == 0:
                        print("Tum testler gecti.")
                    else:
                        print("Bazi testler basarisiz oldu.")
                    time.sleep(5)
            except KeyboardInterrupt:
                print("\n[Test] Izleme durduruldu.")
            except FileNotFoundError:
                print("[Test] pytest yuklu degil. pip install pytest")

        elif islem == "report":
            cikti = args.output or str(PROJE_KOK / "test_report.json")
            print(f"[Test] Test raporu olusturuluyor: {cikti}")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--tb=short", "-q", "--json-report"],
                cwd=str(PROJE_KOK), capture_output=True, text=True
            )
            rapor = {
                "tarih": datetime.now().isoformat(),
                "proje": str(PROJE_KOK),
                "cikti": result.stdout,
                "hata": result.stderr if result.stderr else "",
                "returncode": result.returncode,
                "basari": result.returncode == 0,
            }
            with open(cikti, "w", encoding="utf-8") as f:
                json.dump(rapor, f, indent=2, ensure_ascii=False)
            print(f"[Test] Rapor kaydedildi: {cikti}")
            if result.returncode == 0:
                print("[Test] Tum testler gecti.")
            else:
                print("[Test] Bazi testler basarisiz oldu.")
                print(result.stdout)

    except Exception as e:
        print(f"[Test] Beklenmeyen hata: {e}")
