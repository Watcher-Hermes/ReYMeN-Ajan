#!/usr/bin/env python3
"""Lazy import testi."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_lazy_import_calisiyor_mu():
    """Lazy import mekanizmasının çalıştığını doğrula."""
    from reymen.sistem import main as reymen_main
    
    # _lazy_imports sözlüğü tanımlı olmalı
    assert hasattr(reymen_main, '_lazy_imports')
    assert len(reymen_main._lazy_imports) == 10
    
    print("✅ Lazy import sözlüğü mevcut")


def test_beyin_lazy():
    """Beyin modülünün lazy yüklendiğini doğrula."""
    from reymen.sistem import main as reymen_main
    
    start = time.time()
    Beyin = reymen_main._lazy_import('RuntimeProvider')
    sure = time.time() - start
    
    assert Beyin is not None
    assert sure < 1.0  # 1 saniyeden kısa olmalı
    
    print(f"✅ Beyin lazy import: {sure:.3f}s")


def test_motor_lazy():
    """Motor modülünün lazy yüklendiğini doğrula."""
    from reymen.sistem import main as reymen_main
    
    start = time.time()
    Motor = reymen_main._lazy_import('Motor')
    sure = time.time() - start
    
    assert Motor is not None
    assert sure < 1.0
    
    print(f"✅ Motor lazy import: {sure:.3f}s")


def test_import_hizi():
    """Import hızının iyileştiğini doğrula."""
    from reymen.sistem import main as reymen_main
    
    # Tüm lazy modülleri yükle
    start = time.time()
    for name in reymen_main._lazy_imports:
        reymen_main._lazy_import(name)
    toplam = time.time() - start
    
    # 10 modül 2 saniyeden kısa sürede yüklenmeli
    assert toplam < 2.0
    
    print(f"✅ 10 modül toplam: {toplam:.3f}s")


if __name__ == "__main__":
    test_lazy_import_calisiyor_mu()
    test_beyin_lazy()
    test_motor_lazy()
    test_import_hizi()
    print("\n🎉 Tüm lazy import testleri başarılı!")
