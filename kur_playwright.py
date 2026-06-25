#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLAYWRIGHT OTOMATIK KURULUM - hermes/reymen agent icin.

Kullanim:
  python kur_playwright.py
"""

import sys
import subprocess


def baslik(metin):
    print("\n" + "-" * 60)
    print(f"  {metin}")
    print("-" * 60)


def komut_calistir(argv, aciklama):
    print(f"\n> {aciklama}")
    print(f"  Komut: {' '.join(argv)}\n")
    sonuc = subprocess.run(argv)
    if sonuc.returncode == 0:
        print(f"\n[OK] Basarili: {aciklama}")
        return True
    else:
        print(f"\n[FAIL] Basarisiz (kod {sonuc.returncode}): {aciklama}")
        return False


def main():
    py = sys.executable

    baslik("ORTAM KONTROLU")
    print(f"Aktif Python : {py}")
    print(f"Surum        : {sys.version.split()[0]}")

    if "venv" in py.lower() or "hermes" in py.lower():
        print("[OK] Sanal ortam (venv) icindesin.")
    else:
        print("[UYARI] Global Python gibi gorunuyor.")
        cevap = input("  Yine de devam edeyim mi? (e/h): ").strip().lower()
        if cevap != "e":
            print("Iptal edildi.")
            return 1

    baslik("ADIM 1/3 - pip hazirligi")
    komut_calistir([py, "-m", "pip", "install", "--upgrade", "pip"],
                   "pip guncelleniyor")

    baslik("ADIM 2/3 - playwright paketi kuruluyor")
    if not komut_calistir([py, "-m", "pip", "install", "playwright"],
                          "playwright paketi"):
        print("\nKurulum basarisiz.")
        return 1

    baslik("ADIM 3/3 - chromium tarayicisi indiriliyor")
    if not komut_calistir([py, "-m", "playwright", "install", "chromium"],
                          "chromium indiriliyor"):
        print("\nChromium indirilemedi.")
        return 1

    baslik("DOGRULAMA")
    test_kodu = (
        "from playwright.sync_api import sync_playwright\n"
        "with sync_playwright() as p:\n"
        "    b = p.chromium.launch(headless=True)\n"
        "    pg = b.new_page()\n"
        "    pg.goto('https://example.com')\n"
        "    print('SAYFA BASLIGI:', pg.title())\n"
        "    b.close()\n"
    )
    sonuc = subprocess.run([py, "-c", test_kodu], capture_output=True, text=True)
    if sonuc.returncode == 0 and "SAYFA BASLIGI" in sonuc.stdout:
        print("[OK] TEST GECTI:")
        print("  ", sonuc.stdout.strip())
        baslik("KURULUM TAMAMLANDI")
        return 0
    else:
        print("[FAIL] Test basarisiz:")
        print(sonuc.stdout)
        print(sonuc.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
