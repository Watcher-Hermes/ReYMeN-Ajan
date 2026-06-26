# -*- coding: utf-8 -*-
"""
test_redact.py — redact.py (PII temizleme) testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/guvenlik/test_redact.py
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
    print("ReYMeN - redact.py PII Temizleme Testleri")
    print("=" * 60)

    # 1. email_temizle
    print("\n[1] email_temizle")
    def t1():
        from reymen.guvenlik.redact import email_temizle
        r = email_temizle("ornek@mail.com")
        return r == "[EMAIL]"
    test("email_temizle", "Basit email", t1)

    def t1b():
        from reymen.guvenlik.redact import email_temizle
        r = email_temizle("kullanici@domain.co.uk")
        return r == "[EMAIL]"
    test("email_temizle", "Cok parcali domain", t1b)

    def t1c():
        from reymen.guvenlik.redact import email_temizle
        r = email_temizle("Bu bir test yazisidir")
        return r == "Bu bir test yazisidir"
    test("email_temizle", "PII yok, dokunma", t1c)

    def t1d():
        from reymen.guvenlik.redact import email_temizle
        r = email_temizle("")
        return r == ""
    test("email_temizle", "Bos girdi", t1d)

    def t1e():
        from reymen.guvenlik.redact import email_temizle
        r = email_temizle(None)
        return r is None
    test("email_temizle", "None girdi", t1e)

    # 2. telefon_temizle
    print("\n[2] telefon_temizle")
    def t2():
        from reymen.guvenlik.redact import telefon_temizle
        r = telefon_temizle("Telefon: 5321234567")
        return "[TELEFON]" in r
    test("telefon_temizle", "10 hane", t2)

    def t2b():
        from reymen.guvenlik.redact import telefon_temizle
        r = telefon_temizle("9 haneli: 123456789")
        return "123456789" in r  # 9 hane temizlenmez
    test("telefon_temizle", "9 hane temizlenmez", t2b)

    def t2c():
        from reymen.guvenlik.redact import telefon_temizle
        r = telefon_temizle("0 ile baslayan: 0123456789")
        return "0123456789" in r  # 0 ile baslayan 10 hane temizlenmez
    test("telefon_temizle", "0 ile baslayan 10 hane", t2c)

    # 3. kart_temizle
    print("\n[3] kart_temizle")
    def t3():
        from reymen.guvenlik.redact import kart_temizle
        r = kart_temizle("Kart: 4532015112830366")
        return "[KART_NO]" in r
    test("kart_temizle", "16 hane bitisik", t3)

    def t3b():
        from reymen.guvenlik.redact import kart_temizle
        r = kart_temizle("Kart: 4532-0151-1283-0366")
        return "[KART_NO]" in r
    test("kart_temizle", "Tireli format", t3b)

    def t3c():
        from reymen.guvenlik.redact import kart_temizle
        r = kart_temizle("Kart: 4532 0151 1283 0366")
        return "[KART_NO]" in r
    test("kart_temizle", "Bosluklu format", t3c)

    # 4. api_key_temizle
    print("\n[4] api_key_temizle")
    def t4():
        from reymen.guvenlik.redact import api_key_temizle
        r = api_key_temizle("API_KEY=sk-abc123xyz")
        return "[GIZLI]" in r
    test("api_key_temizle", "API_KEY pattern", t4)

    def t4b():
        from reymen.guvenlik.redact import api_key_temizle
        r = api_key_temizle("TOKEN=gAAAAABns")
        return "[GIZLI]" in r
    test("api_key_temizle", "TOKEN pattern", t4b)

    def t4c():
        from reymen.guvenlik.redact import api_key_temizle
        r = api_key_temizle("PASSWORD=sup3rS3cr3t")
        return "[GIZLI]" in r
    test("api_key_temizle", "PASSWORD pattern", t4c)

    def t4d():
        from reymen.guvenlik.redact import api_key_temizle
        r = api_key_temizle("ACCESS_TOKEN=ghp_abc123")
        return "[GIZLI]" in r
    test("api_key_temizle", "ACCESS_TOKEN pattern", t4d)

    # 5. tc_temizle
    print("\n[5] tc_temizle")
    def t5():
        from reymen.guvenlik.redact import tc_temizle
        r = tc_temizle("TC: 12345678901")
        return "[TC_KIMLIK]" in r
    test("tc_temizle", "Gecerli TC", t5)

    def t5b():
        from reymen.guvenlik.redact import tc_temizle
        r = tc_temizle("Gecersiz: 01234567890")
        return "01234567890" in r  # 0 ile baslayan temizlenmez
    test("tc_temizle", "0 ile baslayan gecersiz", t5b)

    def t5c():
        from reymen.guvenlik.redact import tc_temizle
        r = tc_temizle("Kisa: 12345")
        return "12345" in r
    test("tc_temizle", "11 haneden kisa", t5c)

    # 6. ip_temizle (YENI)
    print("\n[6] ip_temizle")
    def t6():
        from reymen.guvenlik.redact import ip_temizle
        r = ip_temizle("Sunucu: 192.168.1.1")
        return "[IP_ADRESI]" in r
    test("ip_temizle", "Private IP", t6)

    def t6b():
        from reymen.guvenlik.redact import ip_temizle
        r = ip_temizle("Public: 8.8.8.8")
        return "[IP_ADRESI]" in r
    test("ip_temizle", "Public IP", t6b)

    def t6c():
        from reymen.guvenlik.redact import ip_temizle
        r = ip_temizle("Gecersiz: 999.999.999.999")
        return "999.999.999.999" in r  # gecersiz IP, dokunma
    test("ip_temizle", "Gecersiz IP dokunma", t6c)

    def t6d():
        from reymen.guvenlik.redact import ip_temizle
        r = ip_temizle("Local: 0.0.0.0")
        return "0.0.0.0" in r  # ozel, dokunma
    test("ip_temizle", "0.0.0.0 dokunma", t6d)

    # 7. url_param_temizle (YENI)
    print("\n[7] url_param_temizle")
    def t7():
        from reymen.guvenlik.redact import url_param_temizle
        r = url_param_temizle("https://api.site.com/data?api_key=abc123")
        return "[GIZLI]" in r
    test("url_param_temizle", "api_key parametresi", t7)

    def t7b():
        from reymen.guvenlik.redact import url_param_temizle
        r = url_param_temizle("https://site.com/auth?token=eyJhbGci&kullanici=ali")
        return "[GIZLI]" in r and "kullanici=ali" in r
    test("url_param_temizle", "token parametresi, digerleri kalsin", t7b)

    def t7c():
        from reymen.guvenlik.redact import url_param_temizle
        r = url_param_temizle("https://site.com/page?q=arama")
        return "q=arama" in r  # normal query, dokunma
    test("url_param_temizle", "Normal parametre dokunma", t7c)

    # 8. hassas_yol_temizle (YENI)
    print("\n[8] hassas_yol_temizle")
    def t8():
        from reymen.guvenlik.redact import hassas_yol_temizle
        r = hassas_yol_temizle("C:\\Users\\admin\\.ssh\\id_rsa")
        return "[HASSAS_YOL]" in r
    test("hassas_yol_temizle", "Windows .ssh/id_rsa", t8)

    def t8b():
        from reymen.guvenlik.redact import hassas_yol_temizle
        r = hassas_yol_temizle("/home/user/.ssh/id_rsa")
        return "[HASSAS_YOL]" in r
    test("hassas_yol_temizle", "Unix .ssh/id_rsa", t8b)

    def t8c():
        from reymen.guvenlik.redact import hassas_yol_temizle
        r = hassas_yol_temizle("/tmp/README.txt")
        return "/tmp/README.txt" in r  # hassas degil
    test("hassas_yol_temizle", "Normal dosya dokunma", t8c)

    # 9. tam_temizle (entegrasyon)
    print("\n[9] tam_temizle")
    def t9():
        from reymen.guvenlik.redact import tam_temizle
        r = tam_temizle("ornek@mail.com ve API_KEY=sk-abc 192.168.1.1")
        return "[EMAIL]" in r and "[GIZLI]" in r and "[IP_ADRESI]" in r
    test("tam_temizle", "Karma PII", t9)

    def t9b():
        from reymen.guvenlik.redact import tam_temizle
        r = tam_temizle("Bos yazi")
        return r == "Bos yazi"
    test("tam_temizle", "PII yok, dokunma", t9b)

    def t9c():
        from reymen.guvenlik.redact import tam_temizle
        r = tam_temizle("")
        return r == ""
    test("tam_temizle", "Bos girdi", t9c)

    def t9d():
        from reymen.guvenlik.redact import tam_temizle
        r = tam_temizle("Bu bir test", ekstra=("test",))
        return "[GIZLI]" in r
    test("tam_temizle", "Ekstra kelime", t9d)

    # 10. pii_raporu (YENI)
    print("\n[10] pii_raporu")
    def t10():
        from reymen.guvenlik.redact import pii_raporu
        r = pii_raporu("ornek@mail.com")
        return r.get("email") == 1
    test("pii_raporu", "Email tespiti", t10)

    def t10b():
        from reymen.guvenlik.redact import pii_raporu
        r = pii_raporu("ornek@mail.com ve test@site.com ve 5321234567")
        return r.get("email") == 2 and r.get("telefon") == 1
    test("pii_raporu", "Coklu PII tespiti", t10b)

    def t10c():
        from reymen.guvenlik.redact import pii_raporu
        r = pii_raporu("")
        return r == {}
    test("pii_raporu", "Bos girdi", t10c)

    def t10d():
        from reymen.guvenlik.redact import pii_raporu
        r = pii_raporu("Sadece duz yazi")
        return r == {}
    test("pii_raporu", "PII yok", t10d)

    # 11. Import test (motor.py uyumluluk)
    print("\n[11] Motor Uyumluluk")
    def t11():
        from reymen.guvenlik.redact import tam_temizle
        # motor.py su sekilde kullaniyor: from redact import tam_temizle as _pii_temizle
        _pii_temizle = tam_temizle
        r = _pii_temizle("Test: ornek@mail.com")
        return "[EMAIL]" in r
    test("motor_uyum", "tam_temizle alias", t11)

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
