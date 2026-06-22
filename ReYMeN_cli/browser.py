# -*- coding: utf-8 -*-
"""ReYMeN_cli/browser.py — Tarayici CLI.

Web tarayicisini acma, kapama, gezinti, ekran goruntusu alma
ve acik sekmeleri listeleme islemleri.
"""

import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Browser CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: open, close, navigate, screenshot, list
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["open", "close", "navigate", "screenshot", "list"],
                            help="Yapilacak islem (open|close|navigate|screenshot|list)")
    alt_parser.add_argument("--url", type=str, default=None,
                            help="Acilacak/gezilecek URL")
    alt_parser.add_argument("--browser", type=str, default=None,
                            help="Tarayici adi (chrome, firefox, edge)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Ekran goruntusu cikti dosyasi")


def calistir(args):
    """Browser komutunu calistir."""
    try:
        islem = args.islem or "list"
        tarayici = args.browser or "chrome"

        if islem == "open":
            url = args.url or "about:blank"
            print(f"[Browser] {tarayici} ile aciliyor: {url}")
            if sys.platform == "win32":
                subprocess.Popen(["start", url], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            print(f"[Browser] Tarayici acildi: {url}")

        elif islem == "close":
            print(f"[Browser] {tarayici} kapatiliyor...")
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", f"{tarayici}.exe"],
                               capture_output=True)
            elif sys.platform == "darwin":
                subprocess.run(["pkill", "-f", tarayici])
            else:
                subprocess.run(["pkill", "-f", tarayici])
            print(f"[Browser] {tarayici} kapatildi.")

        elif islem == "navigate":
            url = args.url
            if not url:
                print("[Browser] Lutfen --url parametresini belirtin.")
                return
            print(f"[Browser] {url} sayfasina gidiliyor...")
            if sys.platform == "win32":
                subprocess.Popen(["start", url], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            print(f"[Browser] {url} acildi.")

        elif islem == "screenshot":
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
            except ImportError:
                print("[Browser] selenium yuklu degil. pip install selenium")
                return
            url = args.url or "about:blank"
            cikti = args.output or str(PROJE_KOK / "screenshot.png")
            print(f"[Browser] Ekran goruntusu aliniyor: {url}")
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            try:
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                driver.save_screenshot(cikti)
                driver.quit()
                print(f"[Browser] Ekran goruntusu kaydedildi: {cikti}")
            except Exception as e:
                print(f"[Browser] Selenium hatasi: {e}")

        elif islem == "list":
            print("[Browser] Acik tarayici sekmeleri:")
            if sys.platform == "win32":
                try:
                    result = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                        capture_output=True, text=True
                    )
                    if "chrome.exe" in result.stdout:
                        print("  Chrome: calisiyor")
                    result = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq firefox.exe"],
                        capture_output=True, text=True
                    )
                    if "firefox.exe" in result.stdout:
                        print("  Firefox: calisiyor")
                except Exception:
                    print("  (Tespit edilemedi)")
            else:
                try:
                    result = subprocess.run(
                        ["ps", "aux"], capture_output=True, text=True
                    )
                    for satir in result.stdout.split("\n"):
                        for b in ["chrome", "firefox", "msedge"]:
                            if b in satir.lower():
                                print(f"  {b}: calisiyor")
                                break
                except Exception:
                    print("  (Tespit edilemedi)")

    except Exception as e:
        print(f"[Browser] Beklenmeyen hata: {e}")
