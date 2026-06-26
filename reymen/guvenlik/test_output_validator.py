# -*- coding: utf-8 -*-
"""
test_output_validator.py — output_validator.py testleri.

Calistirma:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/guvenlik/test_output_validator.py
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
    print("ReYMeN - OutputValidator Testleri")
    print("=" * 60)

    # ── 1. ValidationResult ─────────────────────────────────────────
    print("\n[1] ValidationResult — veri sinifi")
    def t1():
        from reymen.guvenlik.output_validator import ValidationResult
        vr = ValidationResult(kural_adi="test", gecti=True, mesaj="ok")
        return vr.kural_adi == "test" and vr.gecti is True and vr.mesaj == "ok"
    def t2():
        from reymen.guvenlik.output_validator import ValidationResult
        vr = ValidationResult(kural_adi="test", gecti=False)
        return str(vr) == "[-] test: "
    def t3():
        from reymen.guvenlik.output_validator import ValidationResult
        vr = ValidationResult(kural_adi="test", gecti=True, mesaj="tamam")
        return "[+]" in str(vr) and "test" in str(vr) and "tamam" in str(vr)
    test("ValidationResult", "basic creation", t1)
    test("ValidationResult", "basarisiz repr", t2)
    test("ValidationResult", "basarili repr", t3)

    # ── 2. ValidationReport ──────────────────────────────────────────
    print("\n[2] ValidationReport — rapor sinifi")
    def t4():
        from reymen.guvenlik.output_validator import ValidationReport, ValidationResult
        vr = ValidationReport(gecti=True)
        return vr.gecti is True and vr.sonuclar == [] and vr.hedef == ""
    def t5():
        from reymen.guvenlik.output_validator import ValidationReport, ValidationResult
        vr = ValidationReport(gecti=True, hedef="test_islem")
        vr.sonuclar.append(ValidationResult("k1", True))
        vr.sonuclar.append(ValidationResult("k2", False))
        return len(vr.basarisizlar) == 1 and vr.basarisizlar[0].kural_adi == "k2"
    def t6():
        from reymen.guvenlik.output_validator import ValidationReport, ValidationResult
        vr = ValidationReport(gecti=True, hedef="test")
        vr.sonuclar.append(ValidationResult("k1", True))
        vr.sonuclar.append(ValidationResult("k2", True))
        ozet = vr.ozet()
        return "[+]" in ozet and "2/2" in ozet
    def t7():
        from reymen.guvenlik.output_validator import ValidationReport, ValidationResult
        vr = ValidationReport(gecti=False, hedef="test")
        vr.sonuclar.append(ValidationResult("k1", True))
        vr.sonuclar.append(ValidationResult("k2", False))
        ozet = vr.ozet()
        return "[-]" in ozet and "1/2" in ozet
    def t8():
        from reymen.guvenlik.output_validator import ValidationReport
        vr = ValidationReport(gecti=True, hedef="ornek")
        r = repr(vr)
        return "ValidationReport" in r and "ornek" in r
    test("ValidationReport", "bos rapor", t4)
    test("ValidationReport", "basarisizlar property", t5)
    test("ValidationReport", "ozet basarili", t6)
    test("ValidationReport", "ozet basarisiz", t7)
    test("ValidationReport", "repr", t8)

    # ── 3. OutputValidator: kurulum ──────────────────────────────────
    print("\n[3] OutputValidator — kurulum")
    def t9():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        return v._min_kod == 0 and v._maks_uzunluk == 0 and v._min_uzunluk == 0
    def t10():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=2, maks_uzunluk=500, min_uzunluk=10)
        return v._min_kod == 2 and v._maks_uzunluk == 500 and v._min_uzunluk == 10
    def t11():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        return len(v._hassas_re) == 6
    test("OutputValidator", "varsayilan parametreler", t9)
    test("OutputValidator", "ozel parametreler", t10)
    test("OutputValidator", "hassas regex sayisi", t11)

    # ── 4. OutputValidator: hassas bilgi tespiti ────────────────────
    print("\n[4] dogrula — hassas bilgi")
    def t12():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "API key: sk-abc123def456ghi789jkl012")
        return not r.gecti and "API_KEY" in r.basarisizlar[0].mesaj
    def t13():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir",
            "Private key: -----BEGIN RSA PRIVATE KEY-----\nAAAA")
        return not r.gecti and "PRIVATE_KEY" in r.basarisizlar[0].mesaj
    def t14():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "Token: ghp_abcdefghijklmnopqrstuvwxyz1234567890")
        return not r.gecti and "GITHUB_TOKEN" in r.basarisizlar[0].mesaj
    def t15():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "AWS key: AKIAIOSFODNN7EXAMPLE")
        return not r.gecti and "AWS_KEY" in r.basarisizlar[0].mesaj
    def t16():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.abc123def456ghi789jklmno")
        return not r.gecti and "JWT" in r.basarisizlar[0].mesaj
    def t17():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "Slack: xoxb-123456789012-1234567890123-abcABC")
        return not r.gecti and "SLACK_TOKEN" in r.basarisizlar[0].mesaj
    def t18():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "Normal metin burada boss")
        return r.gecti is True
    test("OutputValidator", "API key tespiti", t12)
    test("OutputValidator", "private key tespiti", t13)
    test("OutputValidator", "github token tespiti", t14)
    test("OutputValidator", "AWS key tespiti", t15)
    test("OutputValidator", "JWT tespiti", t16)
    test("OutputValidator", "slack token tespiti", t17)
    test("OutputValidator", "temiz metin gecer", t18)

    # ── 5. OutputValidator: hata kalibi tespiti ─────────────────────
    print("\n[5] dogrula — hata kalibi")
    def t19():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "bulunamadi: dosya kayboldu")
        return not r.gecti and "hata_kalibi" in [s.kural_adi for s in r.basarisizlar]
    def t20():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "timeout: baglanti zamani asti")
        return not r.gecti
    def t21():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "permission denied: yetki yok")
        return not r.gecti
    def t22():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "not found: dosya bulunamadi")
        return not r.gecti
    def t23():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "connection refused: baglanti reddedildi")
        return not r.gecti
    def t24():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "bu bir normal calisma ciktisidir")
        return r.gecti is True
    test("OutputValidator", "hata:dosya bulunamadi", t19)
    test("OutputValidator", "hata:timeout", t20)
    test("OutputValidator", "hata:permission", t21)
    test("OutputValidator", "hata:not found", t22)
    test("OutputValidator", "hata:connection refused", t23)
    test("OutputValidator", "temiz cikti gecer", t24)

    # ── 6. OutputValidator: bos cikti ──────────────────────────────
    print("\n[6] dogrula — bos/anlamsiz cikti")
    def t25():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "")
        return not r.gecti and "bos" in r.basarisizlar[0].mesaj.lower()
    def t26():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "   ")
        return not r.gecti
    def t27():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "ok")
        return not r.gecti
    def t28():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "[]")
        return not r.gecti
    def t29():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "None")
        return not r.gecti
    def t30():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("calistir", "anlamli bir cikti burada")
        return r.gecti is True
    test("OutputValidator", "bos string", t25)
    test("OutputValidator", "sadece bosluk", t26)
    test("OutputValidator", "sadece ok", t27)
    test("OutputValidator", "sadece []", t28)
    test("OutputValidator", "sadece None", t29)
    test("OutputValidator", "anlamli cikti gecer", t30)

    # ── 7. OutputValidator: uzunluk kontrolleri ──────────────────
    print("\n[7] dogrula — uzunluk")
    def t31():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_uzunluk=10, maks_uzunluk=100)
        r = v.dogrula("calistir", "kisa")
        return not r.gecti and "min_uzunluk" in [s.kural_adi for s in r.basarisizlar]
    def t32():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_uzunluk=5, maks_uzunluk=20)
        r = v.dogrula("calistir", "a" * 25)
        return not r.gecti and "maks_uzunluk" in [s.kural_adi for s in r.basarisizlar]
    def t33():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_uzunluk=5, maks_uzunluk=50)
        r = v.dogrula("calistir", "a" * 30)
        return r.gecti is True
    test("OutputValidator", "min uzunluk alti", t31)
    test("OutputValidator", "maks uzunluk ustu", t32)
    test("OutputValidator", "uzunluk araliginda", t33)

    # ── 8. OutputValidator: kod blogu ─────────────────────────────
    print("\n[8] dogrula — kod blogu sayisi")
    def t34():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=1)
        r = v.dogrula("bir kod yaz", "```python\nprint('hello')\n```")
        return r.gecti is True
    def t35():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=2)
        r = v.dogrula("bir fonksiyon yaz", "```python\ndef test():\n    pass\n```")
        return not r.gecti
    def t36():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=0)
        r = v.dogrula("bir fonksiyon yaz", "```python\ndef test():\n    pass\n```")
        return r.gecti is True
    def t37():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=1)
        r = v.dogrula("ornek metin", "merhaba dunya")
        return r.gecti is True  # kod_isteniyor=False, skips
    def t38():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=1)
        r = v.dogrula("bir kod yaz", "sadece metin, kod blogu yok")
        return not r.gecti
    test("OutputValidator", "kod blogu yeterli", t34)
    test("OutputValidator", "kod blogu yetersiz", t35)
    test("OutputValidator", "kod kontrolu devre disi", t36)
    test("OutputValidator", "kod hedefi yok atla", t37)
    test("OutputValidator", "kod hedefi var kod yok", t38)

    # ── 9. engine — duzeltme ────────────────────────────────────
    print("\n[9] engine — cikti duzeltme")
    def t39():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.engine("calistir", "")
        return "[VALIDASYON: Bos cikti" in r
    def t40():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.engine("calistir", "API key: sk-abc123def456ghi789jkl012")
        return "[REDACTED]" in r and "sk-abc123" not in r
    def t41():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.engine("calistir", "Normal metin")
        return r == "Normal metin"
    def t42():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(maks_uzunluk=10)
        r = v.engine("calistir", "a" * 50)
        return len(r) < 100 and "[VALIDASYON: Cikti kesildi" in r
    def t43():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.engine("calistir", "")
        return "[VALIDASYON: Bos cikti" in r
    test("OutputValidator", "engine: bos cikti", t39)
    test("OutputValidator", "engine: hassas maskele", t40)
    test("OutputValidator", "engine: temiz cikti degismez", t41)
    test("OutputValidator", "engine: maks uzunluk kes", t42)
    test("OutputValidator", "engine: None cikti", t43)

    # ── 10. _hassas_tip_etiket ────────────────────────────────────
    print("\n[10] _hassas_tip_etiket — tip belirleme")
    def t44():
        import re
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = re.compile(r"sk-[A-Za-z0-9]{20,}")
        return v._hassas_tip_etiket(r) == "API_KEY"
    def t45():
        import re
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = re.compile(r"-----BEGIN RSA PRIVATE KEY-----")
        return v._hassas_tip_etiket(r) == "PRIVATE_KEY"
    def t46():
        import re
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = re.compile(r"AKIA[0-9A-Z]{16}")
        return v._hassas_tip_etiket(r) == "AWS_KEY"
    def t47():
        import re
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = re.compile(r"bilinmeyen_pattern_12345")
        return v._hassas_tip_etiket(r) == "UNKNOWN"
    test("OutputValidator", "tip: API_KEY", t44)
    test("OutputValidator", "tip: PRIVATE_KEY", t45)
    test("OutputValidator", "tip: AWS_KEY", t46)
    test("OutputValidator", "tip: UNKNOWN", t47)

    # ── 11. dogrula komple ──────────────────────────────────────
    print("\n[11] dogrula — karmasik senaryolar")
    def t48():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=1, min_uzunluk=5)
        r = v.dogrula("bir kod yaz python",
            "```python\nprint('hello')\n```\nBasarili")
        return r.gecti is True
    def t49():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=1, min_uzunluk=5)
        r = v.dogrula("bir kod yaz", "```python\nprint('hello')\n```\nAPI key: sk-abcdefghijklmnopqrstuvwxyz012345")
        return not r.gecti  # hassas bulundu
    def t50():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator()
        r = v.dogrula("", "")
        return not r.gecti  # bos cikti
    def t51():
        from reymen.guvenlik.output_validator import OutputValidator
        v = OutputValidator(min_kod=2)
        hedef = "bir script yaz ve calistir"
        cikti = "```python\nimport os\nprint('a')\n```\n```bash\nls -la\n```"
        r = v.dogrula(hedef, cikti)
        return r.gecti is True
    test("OutputValidator", "karma: tam basarili", t48)
    test("OutputValidator", "karma: hassas bulundu", t49)
    test("OutputValidator", "karma: bos cikti", t50)
    test("OutputValidator", "karma: 2 kod blogu", t51)

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
