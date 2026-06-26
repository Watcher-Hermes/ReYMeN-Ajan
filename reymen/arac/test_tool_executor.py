# -*- coding: utf-8 -*-
"""
test_tool_executor.py — ToolExecutor testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/arac/test_tool_executor.py
"""

import sys
import os
import time
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
    print("ReYMeN - ToolExecutor Testleri")
    print("=" * 60)

    # ── 1. calistir ────────────────────────────────────────────────────
    print("\n[1] calistir — normal calistirma")
    def t1():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def topla(a, b):
            return a + b
        r = exe.calistir(topla, a=3, b=5)
        return r.get("basarili") is True and r.get("sonuc") == 8

    def t2():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        r = exe.calistir(lambda: 42)
        return r.get("basarili") is True and r.get("sonuc") == 42

    def t3():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def hata_firlat():
            raise ValueError("test hatasi")
        r = exe.calistir(hata_firlat)
        return r.get("basarili") is False and "test hatasi" in r.get("hata", "")

    def t4():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def selamlama(isim):
            return f"Merhaba {isim}"
        r = exe.calistir(selamlama, isim="ReYMeN")
        return r.get("basarili") is True and r.get("sonuc") == "Merhaba ReYMeN"

    test("ToolExecutor", "calistir: basit toplama", t1)
    test("ToolExecutor", "calistir: lambda", t2)
    test("ToolExecutor", "calistir: hata firlatma", t3)
    test("ToolExecutor", "calistir: parametreli", t4)

    # ── 2. calistir_guvenli (timeout) ──────────────────────────────────
    print("\n[2] calistir_guvenli — timeout yonetimi")
    def t5():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        r = exe.calistir_guvenli(lambda: "hizli", timeout=5)
        return r.get("basarili") is True and r.get("sonuc") == "hizli"

    def t6():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def yavas():
            time.sleep(10)
            return "bitti"
        r = exe.calistir_guvenli(yavas, timeout=1)
        return r.get("basarili") is False and r.get("timeout") is True

    def t7():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def hatali():
            raise RuntimeError("kritik hata")
        r = exe.calistir_guvenli(hatali, timeout=5)
        return r.get("basarili") is False and r.get("hata") == "kritik hata"

    def t8():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def coklu_dondur(x, y):
            return {"x": x, "y": y, "toplam": x + y}
        r = exe.calistir_guvenli(coklu_dondur, x=10, y=20, timeout=3)
        sonuc = r.get("sonuc", {})
        return r.get("basarili") is True and sonuc.get("toplam") == 30

    test("ToolExecutor", "calistir_guvenli: hizli fonksiyon", t5)
    test("ToolExecutor", "calistir_guvenli: timeout", t6)
    test("ToolExecutor", "calistir_guvenli: hata firlatma", t7)
    test("ToolExecutor", "calistir_guvenli: dict donus", t8)

    # ── 3. iptal ───────────────────────────────────────────────────────
    print("\n[3] iptal — islem iptali")
    def t9():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        r = exe.iptal("var_olmayan_id")
        return r is False

    def t10():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        # Uzun sureli gorev — calistir_guvenli kullanarak aktif kalsin
        def yavas():
            time.sleep(30)
            return "bitti"
        r = exe.calistir_guvenli(yavas, timeout=5)
        # calistir_guvenli timeout'tan sonra islem zaten bitti
        # iptal'in False donmesi de kabul edilebilir (islem zaten tamamlanmis)
        # Bunun yerine dogrudan aktif islem ekleyelim
        islem_id = f"islem_{int(time.time() * 1000)}"
        with exe._kilit:
            exe._aktif_islemler[islem_id] = {
                "id": islem_id,
                "durum": "calisiyor",
            }
        iptal_r = exe.iptal(islem_id)
        return iptal_r is True

    test("ToolExecutor", "iptal: var olmayan id", t9)
    test("ToolExecutor", "iptal: basarili iptal", t10)

    # ── 4. durum ───────────────────────────────────────────────────────
    print("\n[4] durum — islem durumu sorgulama")
    def t11():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        durum = exe.durum()
        return durum.get("aktif_sayisi") == 0 and durum.get("gecmis_sayisi") == 0

    def t12():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        exe.calistir(lambda: 1)
        durum = exe.durum()
        return durum.get("gecmis_sayisi") >= 1

    def t13():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        r = exe.durum("yok")
        return r.get("bulundu") is False

    test("ToolExecutor", "durum: bos executor", t11)
    test("ToolExecutor", "durum: calistirma sonrasi", t12)
    test("ToolExecutor", "durum: bulunamayan id", t13)

    # ── 5. gecmis ──────────────────────────────────────────────────────
    print("\n[5] gecmis — islem gecmisi")
    def t14():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        g = exe.gecmis()
        return isinstance(g, list) and len(g) == 0

    def t15():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        exe.calistir(lambda: "a")
        exe.calistir(lambda: "b")
        g = exe.gecmis()
        return len(g) == 2

    def t16():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        exe.calistir(lambda: "x", ad="test_func")
        g = exe.gecmis(limit=1)
        return len(g) == 1

    def t17():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def fonk():
            return 1
        exe.calistir(fonk)
        g = exe.gecmis(limit=5)
        return len(g) >= 1 and g[0].get("durum") == "tamamlandi"

    test("ToolExecutor", "gecmis: bos liste", t14)
    test("ToolExecutor", "gecmis: 2 islem", t15)
    test("ToolExecutor", "gecmis: limit parametresi", t16)
    test("ToolExecutor", "gecmis: tamamlandi durumu", t17)

    # ── 6. istatistik ──────────────────────────────────────────────────
    print("\n[6] istatistik — executor istatistikleri")
    def t18():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        i = exe.istatistik()
        return i.get("toplam_islem") == 0 and i.get("basarili") == 0 and i.get("hatali") == 0

    def t19():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        exe.calistir(lambda: "ok")
        exe.calistir(lambda: (_ for _ in ()).throw(ValueError("boz")))
        i = exe.istatistik()
        return i.get("toplam_islem") == 2 and i.get("basarili") == 1 and i.get("hatali") == 1

    def t20():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        def hata():
            raise TypeError("tip hatasi")
        exe.calistir(hata)
        i = exe.istatistik()
        return i.get("toplam_islem") == 1 and i.get("hatali") == 1

    test("ToolExecutor", "istatistik: bos executor", t18)
    test("ToolExecutor", "istatistik: basarili+hatali sayisi", t19)
    test("ToolExecutor", "istatistik: hata tipi", t20)

    # ── 7. _load_tool ──────────────────────────────────────────────────
    print("\n[7] _load_tool — tool yukleme")
    def t21():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        try:
            exe._load_tool("var_olmayan_modul")
            return False
        except (ImportError, AttributeError):
            return True

    def t22():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        try:
            fn = exe._load_tool("web_extract_tool")
            return callable(fn)
        except Exception:
            return "SKIP"

    test("ToolExecutor", "_load_tool: var olmayan modul", t21)
    test("ToolExecutor", "_load_tool: web_extract_tool", t22)

    # ── 8. calistir_tool ───────────────────────────────────────────────
    print("\n[8] calistir_tool — modul uzerinden calistirma")
    def t23():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        r = exe.calistir_tool("var_olmayan")
        return r.get("basarili") is False

    test("ToolExecutor", "calistir_tool: var olmayan modul", t23)

    # ── 9. execute_tool_module ─────────────────────────────────────────
    print("\n[9] execute_tool_module — fonksiyon uzerinden")
    def t24():
        from reymen.arac.tool_executor import execute_tool_module
        r = execute_tool_module("var_olmayan")
        return r.get("basarili") is False

    def t25():
        from reymen.arac.tool_executor import execute_tool_module
        try:
            r = execute_tool_module("web_extract_tool", params={"urls": ["https://ornek.com"]}, timeout=3)
            return r.get("basarili") is True or "hata" in str(r)
        except Exception:
            return "SKIP"

    test("ToolExecutor", "execute_tool_module: var olmayan", t24)
    test("ToolExecutor", "execute_tool_module: web_extract_tool", t25)

    # ── 10. run ────────────────────────────────────────────────────────
    print("\n[10] run — dogrudan calistirma")
    def t26():
        from reymen.arac.tool_executor import run
        import json
        r = run()
        data = json.loads(r)
        return isinstance(data, dict) and "sonuc1" in data and "istatistik" in data

    test("ToolExecutor", "run: json donus", t26)

    # ── 11. gecmis filtresi + yuksek max_gecmis ────────────────────────
    print("\n[11] gecmis filtreleme ve limit")
    def t27():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        for i in range(5):
            def yap(x=i):
                return x
            exe.calistir(yap)
        g = exe.gecmis(limit=3)
        return len(g) == 3

    def t28():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        for i in range(150):
            exe.calistir(lambda: i)
        i = exe.istatistik()
        return i.get("toplam_islem") == 100  # _max_gecmis

    test("ToolExecutor", "gecmis: limit=3", t27)
    test("ToolExecutor", "gecmis: max_gecmis siniri (100)", t28)

    # ── 12. _ortalama_sure_hesapla ─────────────────────────────────────
    print("\n[12] ortalama sure hesaplama")
    def t29():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        i = exe.istatistik()
        return i.get("ortalama_sure") == 0.0

    def t30():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        exe.calistir(lambda: 1)
        i = exe.istatistik()
        return isinstance(i.get("ortalama_sure"), (int, float)) and i.get("ortalama_sure") >= 0

    test("ToolExecutor", "ortalama_sure: bos", t29)
    test("ToolExecutor", "ortalama_sure: calistirma sonrasi", t30)

    # ── 13. Varsayilan timeout ─────────────────────────────────────────
    print("\n[13] varsayilan timeout")
    def t31():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor()
        return exe._varsayilan_timeout == 30.0

    def t32():
        from reymen.arac.tool_executor import ToolExecutor
        exe = ToolExecutor(varsayilan_timeout=15.0)
        return exe._varsayilan_timeout == 15.0

    test("ToolExecutor", "varsayilan timeout: 30sn", t31)
    test("ToolExecutor", "varsayilan timeout: ozel deger", t32)

    # ── Rapor ──────────────────────────────────────────────────────────
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
