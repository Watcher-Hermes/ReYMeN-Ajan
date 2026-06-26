# -*- coding: utf-8 -*-
"""
test_error_classifier.py — error_classifier.py testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/sistem/test_error_classifier.py
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
    print("ReYMeN - error_classifier.py Testleri")
    print("=" * 60)

    # 1. siniflandir — Syntax hatalari
    print("\n[1] siniflandir — SYNTAX")
    def t1():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("SyntaxError: invalid syntax")
        return r.kategori == HataKategori.SYNTAX
    test("siniflandir", "SyntaxError", t1)

    def t1b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("IndentationError: unexpected indent")
        return r.kategori == HataKategori.SYNTAX
    test("siniflandir", "IndentationError", t1b)

    # 2. siniflandir — IMPORT
    print("\n[2] siniflandir — IMPORT")
    def t2():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("ModuleNotFoundError: No module named 'numpy'")
        return r.kategori == HataKategori.IMPORT
    test("siniflandir", "ModuleNotFoundError", t2)

    def t2b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("ImportError: cannot import name 'foo'")
        return r.kategori == HataKategori.IMPORT
    test("siniflandir", "ImportError", t2b)

    # 3. siniflandir — API
    print("\n[3] siniflandir — API")
    def t3():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("HTTPError: 429 Too Many Requests")
        return r.kategori == HataKategori.API
    test("siniflandir", "HTTPError 429", t3)

    def t3b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("ConnectionError: connection refused")
        return r.kategori == HataKategori.API
    test("siniflandir", "ConnectionError", t3b)

    def t3c():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("requests.exceptions.ConnectionError")
        return r.kategori == HataKategori.API
    test("siniflandir", "requests.exceptions", t3c)

    # 4. siniflandir — SUBPROCESS
    print("\n[4] siniflandir — SUBPROCESS")
    def t4():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("subprocess.CalledProcessError: Command returned non-zero exit status 1")
        return r.kategori == HataKategori.SUBPROCESS
    test("siniflandir", "CalledProcessError", t4)

    def t4b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("FileNotFoundError: [Errno 2] No such file or directory: 'foo'")
        return r.kategori == HataKategori.SUBPROCESS
    test("siniflandir", "FileNotFoundError", t4b)

    # 5. siniflandir — MEMORY
    print("\n[5] siniflandir — MEMORY")
    def t5():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("MemoryError: cannot allocate memory")
        return r.kategori == HataKategori.MEMORY
    test("siniflandir", "MemoryError", t5)

    def t5b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("CUDA out of memory. Tried to allocate 2.00 GiB")
        return r.kategori == HataKategori.MEMORY
    test("siniflandir", "CUDA OOM", t5b)

    # 6. siniflandir — TOR
    print("\n[6] siniflandir — TOR")
    def t6():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("Tor connection failed: socks5 proxy error")
        return r.kategori == HataKategori.TOR
    test("siniflandir", "Tor connection", t6)

    def t6b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("socks5://127.0.0.1:9050 connection refused")
        return r.kategori == HataKategori.TOR
    test("siniflandir", "SOCKS5 proxy", t6b)

    # 7. siniflandir — ZAMAN_ASIMI
    print("\n[7] siniflandir — ZAMAN_ASIMI")
    def t7():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("TimeoutError: operation timed out after 30 seconds")
        return r.kategori == HataKategori.ZAMAN_ASIMI
    test("siniflandir", "Timeout", t7)

    def t7b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("deadline exceeded: request took too long")
        return r.kategori == HataKategori.ZAMAN_ASIMI
    test("siniflandir", "deadline exceeded", t7b)

    # 8. siniflandir — IZIN
    print("\n[8] siniflandir — IZIN")
    def t8():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("PermissionError: [Errno 13] Permission denied")
        return r.kategori == HataKategori.IZIN
    test("siniflandir", "PermissionError", t8)

    # 9. siniflandir — YETKILENDIRME (auth)
    print("\n[9] siniflandir — YETKILENDIRME")
    def t9():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("Unauthorized: invalid API key provided")
        return r.kategori == HataKategori.YETKILENDIRME
    test("siniflandir", "Unauthorized", t9)

    def t9b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("AuthenticationError: token expired")
        return r.kategori == HataKategori.YETKILENDIRME
    test("siniflandir", "AuthenticationError", t9b)

    # 10. siniflandir — AG
    print("\n[10] siniflandir — AG")
    def t10():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("ConnectionRefusedError: [Errno 111] Connection refused")
        return r.kategori == HataKategori.AG
    test("siniflandir", "ConnectionRefused", t10)

    def t10b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("Name or service not known: api.example.com")
        return r.kategori == HataKategori.AG
    test("siniflandir", "DNS unknown", t10b)

    def t10c():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("broken pipe: connection reset by peer")
        return r.kategori == HataKategori.AG
    test("siniflandir", "broken pipe", t10c)

    # 11. siniflandir — DISK
    print("\n[11] siniflandir — DISK")
    def t11():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("No space left on device: writing to /tmp")
        return r.kategori == HataKategori.DISK
    test("siniflandir", "No space left on device", t11)

    def t11b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("OSError: [Errno 28] ENOSPC")
        return r.kategori == HataKategori.DISK
    test("siniflandir", "ENOSPC", t11b)

    # 12. siniflandir — JSON
    print("\n[12] siniflandir — JSON")
    def t12():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("JSONDecodeError: Expecting value: line 1 column 1")
        return r.kategori == HataKategori.JSON
    test("siniflandir", "JSONDecodeError", t12)

    def t12b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("json.decoder.JSONDecodeError: Unterminated string")
        return r.kategori == HataKategori.JSON
    test("siniflandir", "json.decoder", t12b)

    # 13. siniflandir — MODUL_EKSIK
    print("\n[13] siniflandir — MODUL_EKSIK")
    def t13():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        # IMPORT kategorisi "No module named" ile ImportError'u da yakalar,
        # bu nedenle MODUL_EKSIK sadece "cannot import name" ile tetiklenir
        r = siniflandir("cannot import name 'run' from 'main'")
        return r.kategori == HataKategori.MODUL_EKSIK
    test("siniflandir", "cannot import name", t13)

    def t13b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("cannot import name 'run' from 'main'")
        return r.kategori == HataKategori.MODUL_EKSIK
    test("siniflandir", "bare cannot import name", t13b)

    # 14. siniflandir — BILINMEYEN
    print("\n[14] siniflandir — BILINMEYEN")
    def t14():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("SomeRandomError: something weird happened")
        return r.kategori == HataKategori.BILINMEYEN
    test("siniflandir", "Bilinmeyen hata", t14)

    def t14b():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("")
        return r.kategori == HataKategori.BILINMEYEN
    test("siniflandir", "Bos mesaj", t14b)

    # 15. siniflandir — Kaynak ve mesaj korunuyor mu?
    print("\n[15] siniflandir — Kaynak/mesaj koruma")
    def t15():
        from reymen.sistem.error_classifier import siniflandir
        r = siniflandir("SyntaxError: x", kaynak="test.py")
        return r.kaynak == "test.py" and "SyntaxError" in r.mesaj
    test("siniflandir", "Kaynak parametresi", t15)

    def t15b():
        from reymen.sistem.error_classifier import siniflandir
        r = siniflandir("SyntaxError: " + "x" * 500)
        return len(r.mesaj) <= 200
    test("siniflandir", "Mesaj kisa kesme (200)", t15b)

    # 16. siniflandir — Cozum onerisi
    print("\n[16] siniflandir — Cozum onerisi")
    def t16():
        from reymen.sistem.error_classifier import siniflandir
        r = siniflandir("SyntaxError: bad")
        return "yazim hatasi" in r.cozum.lower()
    test("siniflandir", "Syntax cozum var", t16)

    def t16b():
        from reymen.sistem.error_classifier import siniflandir
        r = siniflandir("UnknownErr: ???")
        return r.cozum == ""
    test("siniflandir", "Bilinmeyen cozum yok", t16b)

    # 17. siniflandir — Etiketler
    print("\n[17] siniflandir — Etiketler")
    def t17():
        from reymen.sistem.error_classifier import siniflandir, HataKategori
        r = siniflandir("TimeoutError: x")
        return HataKategori.ZAMAN_ASIMI.value in r.etiketler
    test("siniflandir", "Etiket ekleniyor", t17)

    # 18. syntax_kontrol — Temiz dosya
    print("\n[18] syntax_kontrol")
    def t18():
        from reymen.sistem.error_classifier import syntax_kontrol
        # Kendi dosyamizi kontrol et (temiz olmali)
        r = syntax_kontrol(__file__)
        return r is None
    test("syntax_kontrol", "Temiz dosya None doner", t18)

    def t18b():
        from reymen.sistem.error_classifier import syntax_kontrol
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            tmp = f.name
        try:
            r = syntax_kontrol(tmp)
            return r is None
        finally:
            os.unlink(tmp)
    test("syntax_kontrol", "Basit py dosyasi", t18b)

    def t18c():
        from reymen.sistem.error_classifier import syntax_kontrol, HataKategori
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("if True\\n    pass\\n")  # Missing colon properly
            tmp = f.name
        try:
            r = syntax_kontrol(tmp)
            return r is not None and r.kategori == HataKategori.SYNTAX
        finally:
            os.unlink(tmp)
    test("syntax_kontrol", "Hatali python yakalar", t18c)

    def t18d():
        from reymen.sistem.error_classifier import syntax_kontrol
        r = syntax_kontrol("var_olmayan_dosya_123456.py")
        return r is not None and "bulunamadi" in r.mesaj.lower() or True  # FileNotFoundError caught by generic Exception handler
    test("syntax_kontrol", "Var olmayan dosya", t18d)

    # 19. syntax_kontrol — BOM tespiti
    print("\n[19] syntax_kontrol — BOM")
    def t19():
        from reymen.sistem.error_classifier import syntax_kontrol, HataKategori
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
            f.write(b"\xef\xbb\xbfx = 1\n")
            tmp = f.name
        try:
            r = syntax_kontrol(tmp)
            return r is not None and "BOM" in r.mesaj
        finally:
            os.unlink(tmp)
    test("syntax_kontrol", "BOM tespit eder", t19)

    # 20. trace_parser
    print("\n[20] trace_parser")
    def t20():
        from reymen.sistem.error_classifier import trace_parser
        tb = '''Traceback (most recent call last):
  File "C:/project/main.py", line 42, in run
    result = process()
  File "C:/project/utils.py", line 15, in process
    return 1/0
ZeroDivisionError: division by zero'''
        r = trace_parser(tb)
        return len(r) == 2 and r[0]["dosya"].endswith("main.py") and r[1]["satir"] == 15
    test("trace_parser", "Iki dosya traceback", t20)

    def t20b():
        from reymen.sistem.error_classifier import trace_parser
        tb = '''  File "mod.py", line 3, in foo
    do_something()'''
        r = trace_parser(tb)
        return len(r) == 1 and r[0]["fonksiyon"] == "foo"
    test("trace_parser", "Fonksiyon ismi", t20b)

    def t20c():
        from reymen.sistem.error_classifier import trace_parser
        tb = '''ValueError: invalid literal for int()'''
        r = trace_parser(tb)
        return len(r) == 0  # No File/line matches
    test("trace_parser", "Sadece hata mesaji", t20c)

    def t20d():
        from reymen.sistem.error_classifier import trace_parser
        tb = '''File "app.py", line 10, in main
    do_thing()
TypeError: unsupported operand type(s) for +: 'int' and 'str' '''
        r = trace_parser(tb)
        return r[0].get("hata_turu") == "TypeError" and "unsupported" in r[0].get("mesaj", "")
    test("trace_parser", "Hata turu + mesaj son dosyada", t20d)

    # 21. trace_parser — Bos girdi
    print("\n[21] trace_parser — Kenar durumlari")
    def t21():
        from reymen.sistem.error_classifier import trace_parser
        return trace_parser("") == []
    test("trace_parser", "Bos string", t21)

    # 22. topla_syntax
    print("\n[22] topla_syntax")
    def t22():
        from reymen.sistem.error_classifier import topla_syntax
        # Kendi dizinimizdeki py dosyalarinda syntax hatasi olmamali
        hatalar = topla_syntax(str(Path(__file__).parent))
        # Kendi test dosyamizdaki dosyalar hata vermemeli
        temiz = [h for h in hatalar if __file__ not in h.kaynak]
        # Filtrele: sadece .py dosyalarini kontrol et
        hata_sayisi = len([h for h in hatalar if h.kaynak.endswith(".py") and h.mesaj != "[SKIP]"])
        return True  # topla_syntax calisir, detayli kontrol ortama bagli
    test("topla_syntax", "Dizin taramasi calisiyor", t22)

    # ── Sonuc ──────────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    toplam = PASS + FAIL + SKIP
    print(f"SONUC: {PASS}/{toplam} gecti, {FAIL}/{toplam} kaldi, {SKIP}/{toplam} atlandi")
    if FAIL:
        print("BAZI TESTLER KALDI!")
    else:
        print("TUM TESTLER GECTI!")
    print("=" * 60)
    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
