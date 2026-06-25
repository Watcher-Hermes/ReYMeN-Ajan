# -*- coding: utf-8 -*-
"""
test_reymen_hermes_duzeltmeler.py — Derinlemesine eksiklik düzeltme testleri.

PowerShell:
    python reymen/sistem/test_reymen_hermes_duzeltmeler.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(os.path.abspath(__file__)).parent.parent.parent
sys.path.insert(0, str(ROOT))

PASS = 0
FAIL = 0
SKIP = 0


def test(ad, aciklama, fn):
    global PASS, FAIL, SKIP
    try:
        r = fn()
        if r == "SKIP":
            SKIP += 1
            print(f"  SKIP | {ad} - {aciklama}")
        elif r:
            PASS += 1
            print(f"  PASS | {ad} - {aciklama}")
        else:
            FAIL += 1
            print(f"  FAIL | {ad} - {aciklama}")
    except Exception as e:
        FAIL += 1
        print(f"  FAIL | {ad} - {aciklama}: {e}")


def main():
    global PASS, FAIL, SKIP
    print("=" * 60)
    print("ReYMeN - Derinlemesine Eksiklik Duzeltme Testleri")
    print("=" * 60)

    # 1. Logging
    print("\n[1] Logging Sistemi")
    def t1():
        from reymen.sistem.reymen_logging import get_logger, setup_logging
        logger = get_logger("test")
        return logger is not None
    test("logging", "Import + get_logger", t1)

    def t1b():
        from reymen.sistem.reymen_logging import get_logger
        logger = get_logger("test2")
        logger.info("Test mesaji")
        return True
    test("logging", "Logger.info()", t1b)

    # 2. Security Hardened
    print("\n[2] Security Hardened")
    def t2():
        from reymen.guvenlik.security_hardened import SecurityGuard
        guard = SecurityGuard()
        izinli, _ = guard.komut_kontrol("ls -la")
        return izinli
    test("security", "Guvenli komut izinli", t2)

    def t2b():
        from reymen.guvenlik.security_hardened import SecurityGuard
        guard = SecurityGuard()
        izinli, _ = guard.komut_kontrol("rm -rf /")
        return not izinli
    test("security", "Tehlikeli komut engellendi", t2b)

    def t2c():
        from reymen.guvenlik.security_hardened import SecurityGuard
        guard = SecurityGuard()
        izinli, _ = guard.yol_kontrol("C:\\Windows\\System32\\cmd.exe")
        return not izinli
    test("security", "Yasakli yol engellendi", t2c)

    def t2d():
        from reymen.guvenlik.security_hardened import SecurityGuard
        guard = SecurityGuard()
        izinli, _ = guard.yol_kontrol(str(Path.home() / "Desktop" / "test.py"), yazma=True)
        return not izinli  # Desktop guvenli dizin degil
    test("security", "Yazma kontrolu", t2d)

    def t2e():
        from reymen.guvenlik.security_hardened import SecurityGuard
        guard = SecurityGuard()
        izinli, _ = guard.xss_kontrol("<script>alert(1)</script>")
        return not izinli
    test("security", "XSS engellendi", t2e)

    # 3. Config Manager
    print("\n[3] Config Manager")
    def t3():
        from reymen.sistem.config_manager import Config, get_config
        cfg = get_config()
        return cfg.get("model") is not None
    test("config", "Varsayilan model", t3)

    def t3b():
        from reymen.sistem.config_manager import Config
        cfg = Config()
        cfg.set("test_key", "test_value")
        return cfg.get("test_key") == "test_value"
    test("config", "Set/Get", t3b)

    def t3c():
        from reymen.sistem.config_manager import Config
        cfg = Config()
        return cfg.get("max_iterations") == 90
    test("config", "Varsayilan degerler", t3c)

    # 4. Lazy Loader
    print("\n[4] Lazy Loader")
    def t4():
        from reymen.sistem.lazy_loader import LazyModule, ModuleRegistry, get_registry
        reg = get_registry()
        return len(reg.status()) > 0
    test("lazy_loader", "Registry olustu", t4)

    def t4b():
        from reymen.sistem.lazy_loader import LazyModule
        requests = LazyModule("requests")
        return requests.is_available()
    test("lazy_loader", "requests mevcut", t4b)

    def t4c():
        from reymen.sistem.lazy_loader import LazyModule
        olmayan = LazyModule("olmayan_modul_xyz")
        return not olmayan.is_available()
    test("lazy_loader", "Olmayan modul algilama", t4c)

    def t4d():
        from reymen.sistem.lazy_loader import get_registry
        reg = get_registry()
        return reg.is_available("todo")
    test("lazy_loader", "todo tool mevcut", t4d)

    # 5. Health Check
    print("\n[5] Health Check")
    def t5():
        from reymen.sistem.health_check import HealthChecker
        checker = HealthChecker()
        rapor = checker.tam_kontrol()
        return rapor["toplam"] > 0
    test("health_check", "Tam kontrol", t5)

    def t5b():
        from reymen.sistem.health_check import HealthChecker
        checker = HealthChecker()
        rapor = checker.tam_kontrol()
        return rapor["basarili"] > rapor["basarisiz"]
    test("health_check", "Basari > Basarisiz", t5b)

    def t5c():
        from reymen.sistem.health_check import HealthChecker
        checker = HealthChecker()
        rapor = checker.tam_kontrol()
        return "saglik_orani" in rapor
    test("health_check", "Saglik orani", t5c)

    # 6. Motor Logging Entegrasyonu
    print("\n[6] Motor Logging")
    def t6():
        from reymen.cereyan.motor import Motor
        return callable(Motor)
    test("motor", "Motor import", t6)

    def t6b():
        from reymen.cereyan import motor
        return hasattr(motor, 'log')
    test("motor", "Motor log attribute", t6b)

    # 7. Mesaj Formatlama
    print("\n[7] Mesaj Formatlama")
    def t7():
        sys.path.insert(0, str(ROOT / "reymen" / "ag"))
        from telegram_bot import _formatla_metin
        test = "Gorev: 1. Kur 2. Test 3. Yayinla"
        r = _formatla_metin(test)
        return "1.\n" in r or "1. " in r.split("\n")[1] if "\n" in r else False
    test("mesaj_format", "Numaralilar satir basinda", t7)

    # 8. Requirements
    print("\n[8] Requirements")
    def t8():
        req_path = ROOT / "requirements.txt"
        return req_path.exists() and "python-dotenv" in req_path.read_text()
    test("requirements", "requirements.txt mevcut", t8)

    # Ozet
    print("\n" + "=" * 60)
    print(f"SONUC: {PASS} PASS | {FAIL} FAIL | {SKIP} SKIP")
    print("=" * 60)
    if FAIL == 0:
        print("\nTUM TESTLER BASARILI!")
    else:
        print(f"\n{FAIL} test basarisiz.")
    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
