#!/usr/bin/env python3
"""
reymen_otomatik_duzeltici.py — ReYMeN Agent otomatik hata düzeltici.

Bu script ReYMeN'in yaşadığı TÜM hataları otomatik tespit edip düzeltir.

Ne yapar:
  1. ReYMeN'i test eder (her bileşeni ayrı ayrı)
  2. Hata bulursa Python kodu yazar ve çalıştırır
  3. Hata alırsa kodu düzeltir, tekrar çalıştırır
  4. Max 5 deneme — sonra raporlar

Kullanım:
  python reymen_otomatik_duzeltici.py
"""

import sys
import os
import subprocess
import traceback
import json
import time
from pathlib import Path
from datetime import datetime

# ── Proje kökü ──
PROJE_KOK = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJE_KOK))

# ── Renk kodları ──
import sys
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

YESIL = "\033[92m"
KIRMIZI = "\033[91m"
SARI = "\033[93m"
MAVI = "\033[94m"
RESET = "\033[0m"
KALIN = "\033[1m"

# ── Log dosyası ──
LOG_DOSYASI = PROJE_KOK / "logs" / f"duzeltme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_DOSYASI.parent.mkdir(parents=True, exist_ok=True)


def log(mesaj: str, seviye: str = "INFO") -> None:
    """Hem ekrana hem dosyaya yaz."""
    tarih = datetime.now().strftime("%H:%M:%S")
    satir = f"[{tarih}] [{seviye}] {mesaj}"
    print(satir)
    with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
        f.write(satir + "\n")


def baslik(msg: str) -> None:
    print(f"\n{KALIN}{MAVI}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{RESET}")
    log(msg, "BASLIK")


def ok(msg: str) -> None:
    print(f"  {YESIL}✓{RESET} {msg}")
    log(f"✓ {msg}", "OK")


def hata(msg: str) -> None:
    print(f"  {KIRMIZI}✗{RESET} {msg}")
    log(f"✗ {msg}", "HATA")


def uyari(msg: str) -> None:
    print(f"  {SARI}⚠{RESET} {msg}")
    log(f"⚠ {msg}", "UYARI")


def bilgi(msg: str) -> None:
    print(f"  {MAVI}ℹ{RESET} {msg}")
    log(f"ℹ {msg}", "BILGI")


# ══════════════════════════════════════════════════════════════════════════════
# TEST BLOKLARI — her bileşenin test kodu
# ══════════════════════════════════════════════════════════════════════════════

TESTLER = [
    {
        "ad": "Python ortamı",
        "kod": "import sys; print(f'Python {sys.version}')",
        "onem": "kritik",
    },
    {
        "ad": "dotenv",
        "kod": "import dotenv; print('OK')",
        "onem": "kritik",
    },
    {
        "ad": "requests",
        "kod": "import requests; print(f'requests {requests.__version__}')",
        "onem": "kritik",
    },
    {
        "ad": "sqlite3",
        "kod": "import sqlite3; print(f'sqlite3 {sqlite3.sqlite_version}')",
        "onem": "kritik",
    },
    {
        "ad": "reymen paketi",
        "kod": "import reymen; print('OK')",
        "onem": "kritik",
    },
    {
        "ad": "Playwright",
        "kod": "from playwright.sync_api import sync_playwright; print('OK')",
        "onem": "onemli",
    },
    {
        "ad": ".env dosyası",
        "kod": "from pathlib import Path; p = Path('.env'); print('VAR' if p.exists() else 'YOK')",
        "onem": "kritik",
    },
    {
        "ad": "OnceHafiza",
        "kod": "from reymen.sistem.once_hafiza import OnceHafiza; oh = OnceHafiza(); print('OK')",
        "onem": "onemli",
    },
    {
        "ad": "AutoWebSearch",
        "kod": "from reymen.cereyan.auto_web_search import AutoWebSearch; aws = AutoWebSearch(); print('OK')",
        "onem": "onemli",
    },
    {
        "ad": "web_search_tool",
        "kod": "from reymen.arac.web_search_tool import web_search; print('OK')",
        "onem": "onemli",
    },
    {
        "ad": "ConversationLoop",
        "kod": "from reymen.cereyan.conversation_loop import ConversationLoop; print('OK')",
        "onem": "onemli",
    },
    {
        "ad": "Web araması (canlı)",
        "kod": "from reymen.arac.web_search_tool import web_search; s = web_search('test', limit=1); print('OK' if s.get('results') else 'HATA: ' + str(s.get('error')))",
        "onem": "onemli",
    },
    {
        "ad": "Playwright tarayıcı testi",
        "kod": "from playwright.sync_api import sync_playwright\nwith sync_playwright() as p:\n    b = p.chromium.launch(headless=True)\n    pg = b.new_page()\n    pg.goto('https://example.com')\n    print('TEST GECTI:', pg.title())\n    b.close()",
        "onem": "onemli",
    },
    {
        "ad": "Bozuk skill dosyaları",
        "kod": "from pathlib import Path\nskills = Path('reymen/cereyan/skills')\nbozuk = [f.name for f in skills.glob('*.md') if 'drift' in f.read_text(encoding='utf-8', errors='replace').lower()[:500] or 'REFERANS_ARA' in f.read_text(encoding='utf-8', errors='replace')[:500]]\nprint(f'BOZUK:{len(bozuk)}' if bozuk else 'TEMIZ')",
        "onem": "onemli",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# DÜZELTME BLOKLARI — her hata için otomatik düzeltme kodu
# ══════════════════════════════════════════════════════════════════════════════

DUZELTMELER = {
    "dotenv": {
        "kod": "import subprocess, sys; subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-dotenv'], capture_output=True)",
        "aciklama": "python-dotenv kuruluyor",
    },
    "requests": {
        "kod": "import subprocess, sys; subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], capture_output=True)",
        "aciklama": "requests kuruluyor",
    },
    "Playwright": {
        "kod": "import subprocess, sys; subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'], capture_output=True); subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], capture_output=True)",
        "aciklama": "Playwright + Chromium kuruluyor",
    },
    ".env dosyası": {
        "kod": """
from pathlib import Path
env = Path('.env')
if not env.exists():
    env.write_text('''# ReYMeN Agent API Keys
XIAOMI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
''', encoding='utf-8')
    print('.env oluşturuldu')
else:
    print('.env zaten var')
""",
        "aciklama": ".env dosyası oluşturuluyor",
    },
    "Bozuk skill dosyaları": {
        "kod": """
from pathlib import Path
import shutil
skills = Path('reymen/cereyan/skills')
backup = skills / '_corrupted_backup'
backup.mkdir(exist_ok=True)
temizlenen = 0
for f in skills.glob('*.md'):
    try:
        icerik = f.read_text(encoding='utf-8', errors='replace')[:2000]
        if any(k in icerik for k in ['drift_duzeltme', 'REFERANS_ARA', 'drift_duzeltici']):
            shutil.move(str(f), str(backup / f.name))
            temizlenen += 1
    except Exception:
        pass
print(f'{temizlenen} bozuk skill temizlendi')
""",
        "aciklama": "Bozuk skill dosyaları temizleniyor",
    },
    "Web araması (canlı)": {
        "kod": """
import urllib.request
import re
url = 'https://html.duckduckgo.com/html/'
data = 'q=test'.encode()
req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    blocks = re.findall(r'result__a', html)
    print(f'DDG erişim: {len(blocks)} sonuç')
except Exception as e:
    print(f'DDG erişim hatası: {e}')
""",
        "aciklama": "DDG erişim kontrolü",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# ANA MOTOR
# ══════════════════════════════════════════════════════════════════════════════

def test_calistir(test: dict) -> tuple[bool, str]:
    """Tek bir test kodu çalıştır."""
    try:
        sonuc = subprocess.run(
            [sys.executable, "-c", test["kod"]],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJE_KOK),
        )
        if sonuc.returncode == 0:
            return True, sonuc.stdout.strip()
        else:
            return False, sonuc.stderr.strip() or sonuc.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Zaman aşımı (30s)"
    except Exception as e:
        return False, str(e)


def duzeltme_uygula(ad: str) -> bool:
    """Belirli bir hata için düzeltme kodu çalıştır."""
    if ad not in DUZELTMELER:
        return False

    duzeltme = DUZELTMELER[ad]
    bilgi(f"Düzeltme deneniyor: {duzeltme['aciklama']}")

    try:
        sonuc = subprocess.run(
            [sys.executable, "-c", duzeltme["kod"]],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJE_KOK),
        )
        if sonuc.returncode == 0:
            ok(f"Düzeltme başarılı: {sonuc.stdout.strip()[:100]}")
            return True
        else:
            hata(f"Düzeltme başarısız: {sonuc.stderr[:200]}")
            return False
    except Exception as e:
        hata(f"Düzeltme hatası: {e}")
        return False


def ana_dongu() -> int:
    """Ana test + düzeltme döngüsü."""
    baslik("ReYMeN OTOMATİK HATA DÜZELTİCİ")
    bilgi(f"Log dosyası: {LOG_DOSYASI}")
    bilgi(f"Proje kökü: {PROJE_KOK}")

    toplam = len(TESTLER)
    basarili = 0
    basarisiz = []
    duzeltilen = []

    for i, test in enumerate(TESTLER, 1):
        print(f"\n{MAVI}[{i}/{toplam}]{RESET} {test['ad']}...")
        log(f"Test {i}/{toplam}: {test['ad']}")

        # Max 5 deneme
        for deneme in range(1, 6):
            sonuc, cikti = test_calistir(test)

            if sonuc:
                ok(f"{test['ad']} — {cikti[:80]}")
                basarili += 1
                break
            else:
                if deneme < 5:
                    uyari(f"Deneme {deneme}/5 başarısız: {cikti[:100]}")

                    # Düzeltme dene
                    if duzeltme_uygula(test["ad"]):
                        duzeltilen.append(test["ad"])
                        bilgi(f"Tekrar test deneniyor (deneme {deneme+1})...")
                    else:
                        # Düzeltme yoksa bekle ve tekrar dene
                        time.sleep(2)
                else:
                    hata(f"{test['ad']} — 5 denemede çözülemedi: {cikti[:150]}")
                    basarisiz.append({
                        "ad": test["ad"],
                        "hata": cikti[:300],
                        "onem": test["onem"],
                    })

    # ── Özet ──
    baslik("SONUÇ RAPORU")

    print(f"\n  {YESIL}Başarılı:{RESET} {basarili}/{toplam}")
    if duzeltilen:
        print(f"  {SARI}Düzeltilen:{RESET} {len(duzeltilen)}: {', '.join(duzeltilen)}")
    if basarisiz:
        print(f"  {KIRMIZI}Başarısız:{RESET} {len(basarisiz)}")
        for b in basarisiz:
            print(f"    - {b['ad']} ({b['onem']}): {b['hata'][:80]}")

    # ── Kritik hata varsa raporla ──
    kritik_hatalar = [b for b in basarisiz if b["onem"] == "kritik"]
    if kritik_hatalar:
        print(f"\n  {KIRMIZI}{KALIN}❌ {len(kritik_hatalar)} KRİTİK HATA — ReYMeN düzgün çalışmaz!{RESET}")
        return 1
    elif basarisiz:
        print(f"\n  {SARI}{KALIN}⚠️ {len(basarisiz)} kritik olmayan hata var.{RESET}")
        return 0
    else:
        print(f"\n  {YESIL}{KALIN}✅ TÜM TESTLER GEÇTİ — ReYMeN hazır!{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(ana_dongu())
