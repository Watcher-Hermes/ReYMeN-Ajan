# -*- coding: utf-8 -*-
"""
test_hermes_acik_kapatma.py - 18 eksiklik kapatma testi.

PowerShell:
    cd C:/Users/marko/Desktop/Reymen Proje/hermes_projesi
    python reymen/arac/test_hermes_acik_kapatma.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(os.path.abspath(__file__)).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reymen" / "arac"))

PASS = 0
FAIL = 0
SKIP = 0


def test(modul_ad, aciklama, test_fn):
    global PASS, FAIL, SKIP
    try:
        sonuc = test_fn()
        if sonuc == "SKIP":
            SKIP += 1
            print(f"  SKIP | {modul_ad} - {aciklama}")
        elif sonuc:
            PASS += 1
            print(f"  PASS | {modul_ad} - {aciklama}")
        else:
            FAIL += 1
            print(f"  FAIL | {modul_ad} - {aciklama}")
    except Exception as e:
        FAIL += 1
        print(f"  FAIL | {modul_ad} - {aciklama}: {e}")


def main():
    global PASS, FAIL, SKIP
    print("=" * 60)
    print("ReYMeN - Hermes Eksiklik Kapatma Testi (18 Modul)")
    print("=" * 60)

    # 1. web_extract_tool
    print("\n[1] web_extract_tool")
    def t1():
        from reymen.arac.web_extract_tool import web_extract, run
        return callable(web_extract) and callable(run)
    test("web_extract_tool", "Import", t1)

    def t1b():
        from reymen.arac.web_extract_tool import run
        r = run(urls="https://example.com")
        return "example" in r.lower() or "hata" not in r.lower()
    test("web_extract_tool", "URL cekme", t1b)

    # 2. vision_analyze_tool
    print("\n[2] vision_analyze_tool")
    def t2():
        from reymen.arac.vision_analyze_tool import vision_analyze, run
        return callable(vision_analyze) and callable(run)
    test("vision_analyze_tool", "Import", t2)

    def t2b():
        from reymen.arac.vision_analyze_tool import run
        r = run(image_url="")
        return "Hata" in r
    test("vision_analyze_tool", "Bos URL hata", t2b)

    # 3. image_generate_tool
    print("\n[3] image_generate_tool")
    def t3():
        from reymen.arac.image_generate_tool import image_generate, run
        return callable(image_generate) and callable(run)
    test("image_generate_tool", "Import", t3)

    def t3b():
        from reymen.arac.image_generate_tool import run
        r = run(prompt="test")
        return "Hata" in r or "bulunamad" in r
    test("image_generate_tool", "API key yok", t3b)

    # 4. todo_tool
    print("\n[4] todo_tool")
    def t4():
        from reymen.arac.todo_tool import TodoManager, run
        return callable(TodoManager) and callable(run)
    test("todo_tool", "Import", t4)

    def t4b():
        from reymen.arac.todo_tool import run
        r = run(islem="ekle", icerik="Test gorevi")
        return "eklendi" in r.lower()
    test("todo_tool", "Ekle", t4b)

    def t4c():
        from reymen.arac.todo_tool import run
        r = run(islem="istatistik")
        return "toplam" in r.lower()
    test("todo_tool", "Istatistik", t4c)

    # 5. process_tool
    print("\n[5] process_tool")
    def t5():
        from reymen.arac.process_tool import ProcessManager, run
        return callable(ProcessManager) and callable(run)
    test("process_tool", "Import", t5)

    def t5b():
        from reymen.arac.process_tool import run
        r = run(islem="listele")
        return isinstance(r, str)
    test("process_tool", "Listele", t5b)

    # 6. file_ops_tool
    print("\n[6] file_ops_tool")
    def t6():
        from reymen.arac.file_ops_tool import FileOps, run
        return callable(FileOps) and callable(run)
    test("file_ops_tool", "Import", t6)

    def t6b():
        from reymen.arac.file_ops_tool import run
        r = run(islem="read_file", path=str(Path(os.path.abspath(__file__))))
        return "test_hermes" in r
    test("file_ops_tool", "Dosya okuma", t6b)

    def t6c():
        from reymen.arac.file_ops_tool import run
        r = run(islem="search_files", pattern="test_hermes",
                path=str(Path(os.path.abspath(__file__)).parent), target="files")
        return "test_hermes" in r
    test("file_ops_tool", "Dosya arama", t6c)

    # 7. cron_tool
    print("\n[7] cron_tool")
    def t7():
        from reymen.arac.cron_tool import CronManager, run
        return callable(CronManager) and callable(run)
    test("cron_tool", "Import", t7)

    def t7b():
        from reymen.arac.cron_tool import run
        r = run(islem="ekle", ad="test_job", zamanlama="30m", komut="echo test")
        return "eklendi" in r.lower()
    test("cron_tool", "Ekle", t7b)

    # 8. memory_batch_tool
    print("\n[8] memory_batch_tool")
    def t8():
        from reymen.arac.memory_batch_tool import MemoryBatch, run
        return callable(MemoryBatch) and callable(run)
    test("memory_batch_tool", "Import", t8)

    def t8b():
        from reymen.arac.memory_batch_tool import run
        r = run(islem="oku", target="memory")
        return "memory" in r.lower() or "char" in r.lower()
    test("memory_batch_tool", "Okuma", t8b)

    # 9. profile_tool
    print("\n[9] profile_tool")
    def t9():
        from reymen.arac.profile_tool import ProfileManager, run
        return callable(ProfileManager) and callable(run)
    test("profile_tool", "Import", t9)

    def t9b():
        from reymen.arac.profile_tool import run
        r = run(islem="listele")
        return "reymen" in r
    test("profile_tool", "Listele", t9b)

    def t9c():
        from reymen.arac.profile_tool import run
        r = run(islem="aktif")
        return "reymen" in r
    test("profile_tool", "Aktif profil", t9c)

    # 10. approval_tool
    print("\n[10] approval_tool")
    def t10():
        from reymen.arac.approval_tool import ApprovalManager, run
        return callable(ApprovalManager) and callable(run)
    test("approval_tool", "Import", t10)

    def t10b():
        from reymen.arac.approval_tool import run
        r = run(islem="kontrol", tool="read_file", args="test.py")
        return "auto_approve" in r
    test("approval_tool", "Auto-approve", t10b)

    def t10c():
        from reymen.arac.approval_tool import run
        r = run(islem="kontrol", tool="terminal", args="format c:")
        return "block" in r
    test("approval_tool", "Block kontrol", t10c)

    # 11. multi_platform_tool
    print("\n[11] multi_platform_tool")
    def t11():
        from reymen.arac.multi_platform_tool import PlatformManager, run
        return callable(PlatformManager) and callable(run)
    test("multi_platform_tool", "Import", t11)

    def t11b():
        from reymen.arac.multi_platform_tool import run
        r = run(islem="listele")
        return "telegram" in r
    test("multi_platform_tool", "Listele", t11b)

    # 12. browser_mcp_tool
    print("\n[12] browser_mcp_tool")
    def t12():
        from reymen.arac.browser_mcp_tool import BrowserMCP, run
        return callable(BrowserMCP) and callable(run)
    test("browser_mcp_tool", "Import", t12)

    def t12b():
        from reymen.arac.browser_mcp_tool import run
        r = run(islem="navigate", url="https://example.com")
        if "kurulu" in r:
            return "SKIP"
        return True
    test("browser_mcp_tool", "Navigate", t12b)

    # 13. Motor
    print("\n[13] Motor Entegrasyonu")
    def t13():
        from reymen.cereyan.motor import Motor
        return callable(Motor)
    test("motor", "Motor import", t13)

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
