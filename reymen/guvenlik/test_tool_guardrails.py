# -*- coding: utf-8 -*-
"""
test_tool_guardrails.py — tool_guardrails.py testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/guvenlik/test_tool_guardrails.py
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
    print("ReYMeN - ToolGuardrails Testleri")
    print("=" * 60)

    # ── 1. ToolGuardrails: kurulum ──────────────────────────────────
    print("\n[1] ToolGuardrails — kurulum")
    def t1():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg._guvenlik_seviyesi == 3 and len(tg._riskli_araclar) == 10
    def t2():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails(riskli_araclar={"TEST"}, yasakli_parametreler={"tehlikeli"})
        return "TEST" in tg._riskli_araclar and "tehlikeli" in tg._yasakli_parametreler
    def t3():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return "KOMUT_CALISTIR" in tg.VARSAYILAN_RISKLI
    test("ToolGuardrails", "varsayilan kurulum", t1)
    test("ToolGuardrails", "ozel parametreler", t2)
    test("ToolGuardrails", "Varsayilan riskli arac", t3)

    # ── 2. kontrolet: guvenli arac ───────────────────────────────
    print("\n[2] kontrolet — guvenli arac")
    def t4():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", parametre="normal")
        return r.get("guvenli") is True
    def t5():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("DOSYA_OKU", dosya="test.txt")
        return r.get("guvenli") is True
    test("ToolGuardrails", "guvenli string arac", t4)
    test("ToolGuardrails", "guvenli DOSYA_OKU", t5)

    # ── 3. kontrolet: riskli arac (izinsiz) ──────────────────────
    print("\n[3] kontrolet — riskli arac izinsiz")
    def t6():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("KOMUT_CALISTIR", komut="ls")
        return r.get("guvenli") is False and "Riskli" in r.get("sebep", "")
    def t7():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("PYTHON_CALISTIR", kod="print('hello')")
        return r.get("guvenli") is False
    def t8():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("DOSYA_YAZ", icerik="test")
        return r.get("guvenli") is False
    test("ToolGuardrails", "KOMUT_CALISTIR engellenir", t6)
    test("ToolGuardrails", "PYTHON_CALISTIR engellenir", t7)
    test("ToolGuardrails", "DOSYA_YAZ engellenir", t8)

    # ── 4. kontrolet: izin verildikten sonra ─────────────────────
    print("\n[4] kontrolet — riskli arac izinli")
    def t9():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("KOMUT_CALISTIR")
        r = tg.kontrolet("KOMUT_CALISTIR", komut="ls")
        return r.get("guvenli") is True and r.get("arac") == "KOMUT_CALISTIR"
    def t10():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("PYTHON_CALISTIR")
        r = tg.kontrolet("PYTHON_CALISTIR", kod="print(1)")
        return r.get("guvenli") is True
    test("ToolGuardrails", "KOMUT_CALISTIR izinli gecer", t9)
    test("ToolGuardrails", "PYTHON_CALISTIR izinli gecer", t10)

    # ── 5. kontrolet: yasakli parametre ──────────────────────────
    print("\n[5] kontrolet — yasakli parametre")
    def t11():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="rm -rf /")
        return r.get("guvenli") is False
    def t12():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="format C:")
        return r.get("guvenli") is False
    def t13():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", sorgu="DROP TABLE users")
        return r.get("guvenli") is False
    def t14():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="shutdown -s -t 0")
        return r.get("guvenli") is False
    test("ToolGuardrails", "rm -rf engellenir", t11)
    test("ToolGuardrails", "format engellenir", t12)
    test("ToolGuardrails", "drop table engellenir", t13)
    test("ToolGuardrails", "shutdown engellenir", t14)

    # ── 6. shell injection kontrolu ─────────────────────────────
    print("\n[6] _shell_injection_kontrol")
    def t15():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="echo test; rm -rf /")
        return r.get("guvenli") is False
    def t16():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="ls -la | grep test")
        return r.get("guvenli") is False
    def t17():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="$(whoami)")
        return r.get("guvenli") is False
    def t18():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", komut="ls -la")
        return r.get("guvenli") is True
    test("ToolGuardrails", "shell ; engellenir", t15)
    test("ToolGuardrails", "shell pipe engellenir", t16)
    test("ToolGuardrails", "shell subcommand engellenir", t17)
    test("ToolGuardrails", "temiz komut gecer", t18)

    # ── 7. path traversal kontrolu ──────────────────────────────
    print("\n[7] path traversal kontrolu")
    def t19():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", yol="../../../etc/passwd")
        return r.get("guvenli") is False
    def t20():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", yol="..\\..\\Windows\\System32\\config")
        return r.get("guvenli") is False
    def t21():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.kontrolet("test_tool", yol="C:\\Users\\test\\dosya.txt")
        return r.get("guvenli") is True
    test("ToolGuardrails", "path traversal Unix engellenir", t19)
    test("ToolGuardrails", "path traversal Windows engellenir", t20)
    test("ToolGuardrails", "normal yol gecer", t21)

    # ── 8. guvenlik seviyesi ────────────────────────────────────
    print("\n[8] guvenlik_seviyesi_ayarla")
    def t22():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.guvenlik_seviyesi_ayarla(5)
        return tg._guvenlik_seviyesi == 5
    def t23():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.guvenlik_seviyesi_ayarla(0)
        return tg._guvenlik_seviyesi == 1  # clamped
    def t24():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.guvenlik_seviyesi_ayarla(10)
        return tg._guvenlik_seviyesi == 5  # clamped
    def t25():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.guvenlik_seviyesi_ayarla(4)
        # seviye 4+ ile yasakli parametre kontrolu calisir
        r = tg.kontrolet("test_tool", komut="rm -rf /")
        return r.get("guvenli") is False
    test("ToolGuardrails", "seviye 5", t22)
    test("ToolGuardrails", "seviye 0 clamp 1", t23)
    test("ToolGuardrails", "seviye 10 clamp 5", t24)
    test("ToolGuardrails", "seviye 4+ rm -rf engellenir", t25)

    # ── 9. izin_ver / izin_kaldir ──────────────────────────────
    print("\n[9] izin_ver / izin_kaldir")
    def t26():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg.izin_ver("TEST_TOOL") is True
    def t27():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("X")
        return "X" in tg._izinli_araclar
    def t28():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("Y")
        tg.izin_kaldir("Y")
        return "Y" not in tg._izinli_araclar
    def t29():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg.izin_kaldir("VAR_OLMAYAN") is True  # discard = no error
    def t30():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("A")
        tg.izin_ver("B")
        liste = tg.izin_verilen_araclar()
        return "A" in liste and "B" in liste
    test("ToolGuardrails", "izin_ver basarili", t26)
    test("ToolGuardrails", "izin_ver ekler", t27)
    test("ToolGuardrails", "izin_kaldir siler", t28)
    test("ToolGuardrails", "izin_kaldir var olmayan", t29)
    test("ToolGuardrails", "izin_verilen_araclar listesi", t30)

    # ── 10. riskli_arac_ekle / riskli_arac_cikar ───────────────
    print("\n[10] riskli_arac_ekle / riskli_arac_cikar")
    def t31():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.riskli_arac_ekle("YENI_RISKLI")
        return r is True and "YENI_RISKLI" in tg._riskli_araclar
    def t32():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.riskli_arac_cikar("KOMUT_CALISTIR")
        return r is True and "KOMUT_CALISTIR" not in tg._riskli_araclar
    def t33():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = tg.riskli_arac_cikar("VAR_OLMAYAN")
        return r is True  # discard = no error
    test("ToolGuardrails", "riskli_arac_ekle", t31)
    test("ToolGuardrails", "riskli_arac_cikar", t32)
    test("ToolGuardrails", "riskli_arac_cikar var olmayan", t33)

    # ── 11. _arac_adi_al ─────────────────────────────────────────
    print("\n[11] _arac_adi_al — arac adi cikarma")
    def t34():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg._arac_adi_al("test") == "TEST"
    def t35():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        def foo():
            pass
        return tg._arac_adi_al(foo) == "FOO"
    def t36():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        class CustomTool:
            pass
        return tg._arac_adi_al(CustomTool()) == "CUSTOMTOOL"
    test("ToolGuardrails", "string ad", t34)
    test("ToolGuardrails", "fonksiyon adi", t35)
    test("ToolGuardrails", "nesne class adi", t36)

    # ── 12. guvenli_mi ──────────────────────────────────────────
    print("\n[12] guvenli_mi")
    def t37():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg.guvenli_mi("test_tool") is True
    def t38():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        return tg.guvenli_mi("KOMUT_CALISTIR") is False
    def t39():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("KOMUT_CALISTIR")
        return tg.guvenli_mi("KOMUT_CALISTIR") is True
    test("ToolGuardrails", "guvenli arac true", t37)
    test("ToolGuardrails", "riskli arac false", t38)
    test("ToolGuardrails", "riskli izinli true", t39)

    # ── 13. engellenen_islemler ─────────────────────────────────
    print("\n[13] engellenen_islemler")
    def t40():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.kontrolet("KOMUT_CALISTIR")
        tg.kontrolet("SIL", hedef="test")
        engel = tg.engellenen_islemler()
        return len(engel) == 2
    def t41():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        for i in range(20):
            tg.kontrolet("KOMUT_CALISTIR", no=i)
        engel = tg.engellenen_islemler(limit=5)
        return len(engel) == 5
    def t42():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.kontrolet("KOMUT_CALISTIR")
        engel = tg.engellenen_islemler()
        return "arac" in engel[0] and "zaman" in engel[0]
    test("ToolGuardrails", "engellenen 2 islem", t40)
    test("ToolGuardrails", "engellenen limit=5", t41)
    test("ToolGuardrails", "engellenen dict anahtarlari", t42)

    # ── 14. istatistik ──────────────────────────────────────────
    print("\n[14] istatistik")
    def t43():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        i = tg.istatistik()
        return i["guvenlik_seviyesi"] == 3 and i["izinli_arac_sayisi"] == 0 and i["engellenen_islem"] == 0
    def t44():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("X")
        tg.izin_ver("Y")
        tg.kontrolet("KOMUT_CALISTIR")
        i = tg.istatistik()
        return i["izinli_arac_sayisi"] == 2 and i["engellenen_islem"] == 1
    def t45():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.riskli_arac_ekle("OZEL")
        i = tg.istatistik()
        return i["riskli_arac_sayisi"] == 11
    test("ToolGuardrails", "bos istatistik", t43)
    test("ToolGuardrails", "2 izinli + 1 engel", t44)
    test("ToolGuardrails", "riskli sayisi 11", t45)

    # ── 15. reset ──────────────────────────────────────────────
    print("\n[15] reset")
    def t46():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("TEST")
        tg.kontrolet("KOMUT_CALISTIR")
        tg.guvenlik_seviyesi_ayarla(5)
        tg.reset()
        i = tg.istatistik()
        return i["guvenlik_seviyesi"] == 3 and i["izinli_arac_sayisi"] == 0 and i["engellenen_islem"] == 0
    test("ToolGuardrails", "reset sifirlar", t46)

    # ── 16. __repr__ ve __str__ ─────────────────────────────────
    print("\n[16] __repr__ / __str__")
    def t47():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        r = repr(tg)
        return "ToolGuardrails" in r and "seviye" in r and "riskli" in r
    def t48():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        s = str(tg)
        return "ToolGuardrails" in s and "seviye=3" in s
    def t49():
        from reymen.guvenlik.tool_guardrails import ToolGuardrails
        tg = ToolGuardrails()
        tg.izin_ver("A")
        tg.kontrolet("KOMUT_CALISTIR")
        s = str(tg)
        return "izinli=1" in s and "engel=1" in s
    test("ToolGuardrails", "__repr__", t47)
    test("ToolGuardrails", "__str__ varsayilan", t48)
    test("ToolGuardrails", "__str__ durumlu", t49)

    # ── Rapor ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    toplam = PASS + FAIL + SKIP
    print(f"Toplam: {toplam} | PASS: {PASS} | FAIL: {FAIL} | SKIP: {SKIP}")
    if FAIL == 0:
        print("✔ TUM TESTLER BASARILI")
    else:
        print(f"✘ {FAIL} test basarisiz")
    print("=" * 60)
    return FAIL == 0


if __name__ == "__main__":
    basarili = main()
    sys.exit(0 if basarili else 1)
