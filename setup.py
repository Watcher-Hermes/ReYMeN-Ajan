# -*- coding: utf-8 -*-
"""
setup.py — ReYMeN Agent kurulum scripti.

Yeni bilgisayarda tek komutla tüm bağımlılıkları kurar:
    python setup.py

Ne yapar:
    1. Python versiyonu kontrolü (>= 3.10)
    2. pip güncelleme
    3. requirements.txt'deki paketler
    4. Playwright + Chromium kurulumu
    5. .env dosyası kontrolü
    6. Veritabanı dizinleri oluşturma
    7. Sağlık kontrolü
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# ── Renk kodları (Windows Terminal) ──────────────────────────────────────────
try:
    os.system("")  # Windows ANSI desteği aktif et
except Exception:
    pass

YESIL = "\033[92m"
KIRMIZI = "\033[91m"
SARI = "\033[93m"
MAVI = "\033[94m"
RESET = "\033[0m"
KALIN = "\033[1m"


def baslik(msg: str) -> None:
    print(f"\n{KALIN}{MAVI}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{RESET}\n")


def ok(msg: str) -> None:
    print(f"  {YESIL}✓{RESET} {msg}")


def hata(msg: str) -> None:
    print(f"  {KIRMIZI}✗{RESET} {msg}")


def uyari(msg: str) -> None:
    print(f"  {SARI}⚠{RESET} {msg}")


def bilgi(msg: str) -> None:
    print(f"  {MAVI}ℹ{RESET} {msg}")


def komut_calistir(cmd: list[str], aciklama: str = "") -> tuple[bool, str]:
    """Komutu çalıştır, sonucu döndür."""
    try:
        sonuc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if sonuc.returncode == 0:
            if aciklama:
                ok(aciklama)
            return True, sonuc.stdout
        else:
            if aciklama:
                hata(f"{aciklama} — HATA: {sonuc.stderr[:200]}")
            return False, sonuc.stderr
    except subprocess.TimeoutExpired:
        hata(f"{aciklama} — ZAMAN AŞIMI (300s)")
        return False, "timeout"
    except FileNotFoundError:
        hata(f"{aciklama} — Komut bulunamadı: {cmd[0]}")
        return False, "not found"


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 1: Python Kontrolü
# ══════════════════════════════════════════════════════════════════════════════

def python_kontrol() -> bool:
    """Python >= 3.10 kontrolü."""
    baslik("ADIM 1: Python Versiyonu Kontrolü")

    versiyon = sys.version_info
    bilgi(f"Python {versiyon.major}.{versiyon.minor}.{versiyon.micro}")

    if versiyon.major < 3 or (versiyon.major == 3 and versiyon.minor < 10):
        hata("Python >= 3.10 gerekli! Lütfen Python'u güncelleyin.")
        return False

    ok(f"Python {versiyon.major}.{versiyon.minor} — uyumlu")
    return True


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 2: pip Güncelleme
# ══════════════════════════════════════════════════════════════════════════════

def pip_guncelle() -> bool:
    """pip'i güncelle."""
    baslik("ADIM 2: pip Güncelleme")

    basarili, _ = komut_calistir(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "pip güncelleniyor",
    )
    return basarili


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 3: requirements.txt Kurulumu
# ══════════════════════════════════════════════════════════════════════════════

def requirements_kur() -> bool:
    """requirements.txt'deki paketleri kur."""
    baslik("ADIM 3: Python Paketleri Kurulumu")

    req_dosyasi = Path(__file__).parent / "requirements.txt"
    if not req_dosyasi.exists():
        uyari("requirements.txt bulunamadı — temel paketler kuruluyor")
        paketler = ["python-dotenv>=1.0.0", "requests>=2.31.0"]
    else:
        # requirements.txt'yi oku, yorum satırlarını filtrele
        with open(req_dosyasi, encoding="utf-8") as f:
            satirlar = f.readlines()

        paketler = []
        for satir in satirlar:
            satir = satir.strip()
            if satir and not satir.startswith("#") and not satir.startswith("\"\"\""):
                # Python yorum satırlarını atla
                if not satir.startswith("ZORUNLU") and not satir.startswith("OPSİYONEL") \
                   and not satir.startswith("TEST") and ">=" in satir or "==" in satir:
                    paketler.append(satir)

    if not paketler:
        bilgi("Kurulacak paket yok")
        return True

    bilgi(f"{len(paketler)} paket kurulacak...")
    for p in paketler:
        basarili, _ = komut_calistir(
            [sys.executable, "-m", "pip", "install", p],
            f"  {p}",
        )
        if not basarili:
            uyari(f"{p} kurulamadı — devam ediliyor")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 4: Playwright + Chromium Kurulumu
# ══════════════════════════════════════════════════════════════════════════════

def playwright_kur() -> bool:
    """Playwright ve Chromium tarayıcısını kur + gerçek tarayıcı testi."""
    baslik("ADIM 4: Playwright + Chromium Kurulumu")

    py = sys.executable

    # ── Venv kontrolü ──
    if "venv" in py.lower() or "hermes" in py.lower():
        ok(f"Sanal ortam tespit edildi: {py}")
    else:
        uyari(f"Global Python gibi görünüyor: {py}")
        bilgi("Reymen'in venv'i ile çalıştırdığından emin olun.")

    # ── 1. pip güncel ──
    komut_calistir([py, "-m", "pip", "install", "--upgrade", "pip"], "pip güncelleme")

    # ── 2. playwright pip paketi ──
    bilgi("Playwright pip paketi kuruluyor...")
    basarili, _ = komut_calistir(
        [py, "-m", "pip", "install", "playwright"],
        "playwright pip paketi",
    )
    if not basarili:
        hata("Playwright pip paketi kurulamadı!")
        return False

    # ── 3. Chromium tarayıcısı ──
    bilgi("Chromium tarayıcısı indiriliyor (birkaç yüz MB, sürebilir)...")
    basarili, _ = komut_calistir(
        [py, "-m", "playwright", "install", "chromium"],
        "Chromium tarayıcısı",
    )
    if not basarili:
        hata("Chromium indirilemedi! İnternet bağlantısını kontrol edin.")
        return False

    # ── 4. GERÇEK TARAYICI TESTİ — sadece import değil, sayfa aç ──
    baslik("DOĞRULAMA: Gerçek tarayıcı testi")
    test_kodu = (
        "from playwright.sync_api import sync_playwright\n"
        "with sync_playwright() as p:\n"
        "    b = p.chromium.launch(headless=True)\n"
        "    pg = b.new_page()\n"
        "    pg.goto('https://example.com')\n"
        "    print('TEST GECTI — SAYFA BASLIGI:', pg.title())\n"
        "    b.close()\n"
    )

    sonuc = subprocess.run(
        [py, "-c", test_kodu],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if sonuc.returncode == 0 and "TEST GECTI" in sonuc.stdout:
        ok(f"Tarayıcı testi başarılı: {sonuc.stdout.strip()}")
        return True
    else:
        hata(f"Tarayıcı testi başarısız!")
        if sonuc.stderr:
            bilgi(f"Hata: {sonuc.stderr[:300]}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 5: .env Dosyası Kontrolü
# ══════════════════════════════════════════════════════════════════════════════

def env_kontrol() -> bool:
    """/.env dosyası kontrolü."""
    baslik("ADIM 5: .env Dosyası Kontrolü")

    env_dosyasi = Path(__file__).parent / ".env"
    if env_dosyasi.exists():
        ok(".env dosyası mevcut")
        return True

    uyari(".env dosyası bulunamadı")
    bilgi("Örnek .env oluşturuluyorn...")

    ornek = """# ReYMeN Agent — API Anahtarları
# Bu dosyayı düzenleyin ve API anahtarlarınızı ekleyin.

# DeepSeek API
DEEPSEEK_API_KEY=

# Xiaomi MiMo API
XIAOMI_API_KEY=

# OpenAI API (opsiyonel)
OPENAI_API_KEY=

# LM Studio (yerel, varsayılan: http://localhost:1234/v1)
LM_STUDIO_URL=http://localhost:1234/v1

# Telegram Bot Token (opsiyonel)
TELEGRAM_BOT_TOKEN=
"""

    with open(env_dosyasi, "w", encoding="utf-8") as f:
        f.write(ornek)

    ok(".env dosyası oluşturuldu — API anahtarlarını düzenleyin")
    return True


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 6: Veritabanı Dizinleri
# ══════════════════════════════════════════════════════════════════════════════

def dizinler_olustur() -> bool:
    """Gerekli dizinleri oluştur."""
    baslik("ADIM 6: Veritabanı Dizinleri")

    proje_kok = Path(__file__).parent
    dizinler = [
        proje_kok / "reymen" / "hafiza",
        proje_kok / "reymen" / "cereyan" / ".ReYMeN",
        proje_kok / "reymen" / "cereyan" / "skills",
        proje_kok / "logs",
    ]

    for d in dizinler:
        d.mkdir(parents=True, exist_ok=True)
        ok(f"  {d.relative_to(proje_kok)}")

    return True


# ══════════════════════════════════════════════════════════════════════════════
# ADIM 7: Sağlık Kontrolü
# ══════════════════════════════════════════════════════════════════════════════

def saglik_kontrol() -> bool:
    """Tüm bileşenlerin çalıştığını doğrula."""
    baslik("ADIM 7: Sağlık Kontrolü")

    kontroller = [
        ("python-dotenv", "import dotenv; print('OK')"),
        ("requests", "import requests; print('OK')"),
        ("sqlite3", "import sqlite3; print('OK')"),
        ("Playwright", "from playwright.sync_api import sync_playwright; print('OK')"),
        ("reymen paketi", "import reymen; print('OK')"),
    ]

    basarili = 0
    for ad, kod in kontroller:
        ok_bool, cikti = komut_calistir(
            [sys.executable, "-c", kod],
            ad,
        )
        if ok_bool:
            basarili += 1

    bilgi(f"{basarili}/{len(kontroller)} bileşen çalışıyor")

    return basarili >= 3  # En az 3 bileşen çalışsın


# ══════════════════════════════════════════════════════════════════════════════
# ANA FONKSİYON
# ══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """ReYMeN Agent kurulumunu başlat."""
    print(f"\n{KALIN}{MAVI}")
    print("  ██████╗ ███████╗██╗   ██╗███╗   ███╗███████╗███╗   ██╗")
    print("  ██╔══██╗██╔════╝╚██╗ ██╔╝████╗ ████║██╔════╝████╗  ██║")
    print("  ██████╔╝█████╗   ╚████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║")
    print("  ██╔══██╗██╔══╝    ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║")
    print("  ██║  ██║███████╗   ██║   ██║ ╚═╝ ██║███████╗██║ ╚████║")
    print("  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝")
    print(f"{RESET}")
    print(f"  {KALIN}ReYMeN Agent — Kurulum Scripti{RESET}")
    print(f"  {SARI}Yeni bilgisayarda tek komutla tüm bağımlılıkları kurar.{RESET}\n")

    adimlar = [
        ("Python Kontrolü", python_kontrol),
        ("pip Güncelleme", pip_guncelle),
        ("Paket Kurulumu", requirements_kur),
        ("Playwright + Chromium", playwright_kur),
        (".env Dosyası", env_kontrol),
        ("Dizinler", dizinler_olustur),
        ("Sağlık Kontrolü", saglik_kontrol),
    ]

    basarili = 0
    for ad, fonksiyon in adimlar:
        try:
            if fonksiyon():
                basarili += 1
        except Exception as e:
            hata(f"{ad} hatası: {e}")

    # ── Özet ──
    baslik("KURULUM ÖZETİ")
    bilgi(f"{basarili}/{len(adimlar)} adım tamamlandı")

    if basarili == len(adimlar):
        print(f"\n  {YESIL}{KALIN}✅ ReYMeN Agent kurulumu tamamlandı!{RESET}")
        print(f"  {SARI}Başlatmak için: python main.py{RESET}\n")
        return 0
    elif basarili >= len(adimlar) - 2:
        print(f"\n  {SARI}{KALIN}⚠️ Kurulum kısmen tamamlandı.{RESET}")
        print(f"  {SARI}Eksik adımları manuel tamamlayın.{RESET}\n")
        return 0
    else:
        print(f"\n  {KIRMIZI}{KALIN}❌ Kurulum başarısız!{RESET}")
        print(f"  {KIRMIZI}Hataları kontrol edin ve tekrar deneyin.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
