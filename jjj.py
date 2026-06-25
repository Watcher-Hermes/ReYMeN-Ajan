#!/usr/bin/env python3
"""
PLAYWRIGHT OTOMATIK KURULUM — hermes/reymen agent için.

Bu script KENDİ çalıştığı Python ortamına kurar. Bu yüzden ÖNEMLİ:
  reymen'in çalıştığı venv'in python.exe'si ile çalıştır, örn:

  & "C:\\Users\\marko\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe" kur_playwright.py

  (Baştaki & ile tam yolu vererek çalıştırırsan doğru ortama kurar.)

Yaptıkları, sırayla:
  1. Hangi Python ortamında olduğunu gösterir (doğru venv mi diye görürsün)
  2. playwright paketini kurar/günceller
  3. chromium tarayıcısını indirir
  4. Kurulumu test eder (gerçekten import edilip çalışıyor mu)
"""

import sys
import subprocess
from pathlib import Path


def baslik(metin):
    print("\n" + "─" * 60)
    print(f"  {metin}")
    print("─" * 60)


def komut_calistir(argv, aciklama):
    """Verilen komutu çalıştırır, çıktıyı canlı gösterir, sonucu döndürür."""
    print(f"\n▶ {aciklama}")
    print(f"  Komut: {' '.join(argv)}\n")
    sonuc = subprocess.run(argv)
    if sonuc.returncode == 0:
        print(f"\n✅ Başarılı: {aciklama}")
        return True
    else:
        print(f"\n❌ Başarısız (kod {sonuc.returncode}): {aciklama}")
        return False


def main():
    py = sys.executable  # BU script'i çalıştıran python.exe — kurulum buraya gider

    baslik("ORTAM KONTROLÜ")
    print(f"Aktif Python : {py}")
    print(f"Sürüm        : {sys.version.split()[0]}")

    # venv kontrolü — doğru ortamda mıyız uyarısı
    if "venv" in py.lower() or "hermes" in py.lower():
        print("✅ Bir sanal ortam (venv) içindesin — doğru görünüyor.")
    else:
        print("⚠️  UYARI: Bu global Python gibi görünüyor.")
        print("   reymen'in venv'i ile çalıştırdığından emin ol, yoksa")
        print("   kurulum yanlış ortama gider ve agent yine bulamaz.")
        cevap = input("\n   Yine de devam ed\u0259yim mi? (e/h): ").strip().lower()
        if cevap != "e":
            print("İptal edildi. Doğru venv ile tekrar çalıştır.")
            return 1

    # 1. pip güncel mi (zorunlu değil ama temiz kurulum için)
    baslik("ADIM 1/3 — pip hazırlığı")
    komut_calistir([py, "-m", "pip", "install", "--upgrade", "pip"],
                   "pip güncelleniyor")

    # 2. playwright paketi
    baslik("ADIM 2/3 — playwright paketi kuruluyor")
    if not komut_calistir([py, "-m", "pip", "install", "playwright"],
                          "playwright paketi"):
        print("\nKurulum başarısız. İnternet/izin sorununu kontrol et.")
        return 1

    # 3. chromium tarayıcısı (birkaç yüz MB — sürebilir)
    baslik("ADIM 3/3 — chromium tarayıcısı indiriliyor (biraz sürebilir)")
    if not komut_calistir([py, "-m", "playwright", "install", "chromium"],
                          "chromium indiriliyor"):
        print("\nChromium indirilemedi. İnternet bağlantısını kontrol et.")
        return 1

    # 4. DOĞRULAMA — gerçekten çalışıyor mu
    baslik("DOĞRULAMA — playwright çalışıyor mu test ediliyor")
    test_kodu = (
        "from playwright.sync_api import sync_playwright\n"
        "with sync_playwright() as p:\n"
        "    b = p.chromium.launch(headless=True)\n"
        "    pg = b.new_page()\n"
        "    pg.goto('https://example.com')\n"
        "    print('SAYFA BASLIGI:', pg.title())\n"
        "    b.close()\n"
    )
    sonuc = subprocess.run([py, "-c", test_kodu],
                           capture_output=True, text=True)
    if sonuc.returncode == 0 and "SAYFA BASLIGI" in sonuc.stdout:
        print("✅ TEST GEÇTİ — playwright çalışıyor:")
        print("  ", sonuc.stdout.strip())
        baslik("KURULUM TAMAMLANDI ✅")
        print("Artık reymen'i çalıştır — TARAYICI_AC fiyatı çekebilmeli.")
        return 0
    else:
        print("❌ Test başarısız:")
        print(sonuc.stdout)
        print(sonuc.stderr)
        print("\nPaket kuruldu ama tarayıcı açılamıyor — chromium indirme")
        print("adımını tekrar çalıştırmayı dene.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
