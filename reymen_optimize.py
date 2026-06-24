#!/usr/bin/env python3
"""
ReYMeN Optimizasyon Scripti v2
Kolay ve güvenli optimizasyonlar.

Kullanım:
    python reymen_optimize.py --all
    python reymen_optimize.py --tool-azalt
    python reymen_optimize.py --test-olustur
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

PROJE_KOK = Path(__file__).parent.resolve()
BACKUP_KOK = PROJE_KOK / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def backup_al(dosya_yolu: Path) -> None:
    """Dosyayı yedekle."""
    if not dosya_yolu.exists():
        return
    hedef = BACKUP_KOK / dosya_yolu.relative_to(PROJE_KOK)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dosya_yolu, hedef)

# ══════════════════════════════════════════════════════════════════════════════
# 1. TOOL AZALTMA
# ══════════════════════════════════════════════════════════════════════════════

CORE_TOOLS = [
    "web_search", "terminal", "file_read", "file_write", "file_edit",
    "memory", "session_search", "skill_view", "skills_list",
]

OPTIONAL_TOOLS = {
    "browser": ["web_extract", "browser_navigate", "browser_click", "browser_type"],
    "vision": ["vision_analyze", "image_generate"],
    "code": ["execute_code", "delegate_task"],
    "media": ["text_to_speech", "audio_transcribe"],
}

def tool_azalt():
    """Tool sayısını azalt."""
    print("\n🔧 Tool Sayısı Azaltılıyor...")
    
    motor_dosya = PROJE_KOK / "reymen" / "cereyan" / "motor.py"
    if not motor_dosya.exists():
        print(f"  ❌ {motor_dosya} bulunamadı")
        return
    
    backup_al(motor_dosya)
    
    # Mevcut dosyayı oku
    with open(motor_dosya, 'r', encoding='utf-8') as f:
        icerik = f.read()
    
    # Tool registry bloğunu ekle (dosyanın sonuna)
    tool_registry = f'''

# ══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED TOOL REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

CORE_TOOLS = {json.dumps(CORE_TOOLS, indent=4)}

OPTIONAL_TOOLS = {json.dumps(OPTIONAL_TOOLS, indent=4)}

def get_active_tools(context=None):
    """Aktif tool'ları döndür."""
    tools = CORE_TOOLS.copy()
    if context:
        if context.get("web"):
            tools.extend(OPTIONAL_TOOLS.get("browser", []))
        if context.get("vision"):
            tools.extend(OPTIONAL_TOOLS.get("vision", []))
        if context.get("code"):
            tools.extend(OPTIONAL_TOOLS.get("code", []))
    return tools

'''
    
    with open(motor_dosya, 'a', encoding='utf-8') as f:
        f.write(tool_registry)
    
    print(f"  ✅ Tool registry güncellendi")
    print(f"  📦 Core: {len(CORE_TOOLS)} tool")

# ══════════════════════════════════════════════════════════════════════════════
# 2. CONFIG BİRLEŞTİRME
# ══════════════════════════════════════════════════════════════════════════════

def config_birlestir():
    """Config dosyalarını basitleştir."""
    print("\n🔧 Config Basitleştiriliyor...")
    
    # setup.json'ı sil
    setup_dosya = PROJE_KOK / "reymen" / "sistem" / ".ReYMeN" / "setup.json"
    if setup_dosya.exists():
        backup_al(setup_dosya)
        
        # setup.json'daki bilgileri oku
        with open(setup_dosya, 'r', encoding='utf-8') as f:
            setup = json.load(f)
        
        # config.yaml'a ekle
        config_dosya = PROJE_KOK / "config.yaml"
        with open(config_dosya, 'r', encoding='utf-8') as f:
            config = f.read()
        
        # Preferred provider ekle
        if "preferred_provider" not in config and "tercih_provider" in setup:
            config += f"\n# Otomatik eklendi (setup.json'dan)\n"
            config += f"preferred_provider: {setup['tercih_provider']}\n"
            config += f"preferred_model: {setup['tercih_model']}\n"
            
            with open(config_dosya, 'w', encoding='utf-8') as f:
                f.write(config)
        
        setup_dosya.unlink()
        print(f"  🗑️  setup.json silindi")
    
    print(f"  ✅ Config basitleştirildi")

# ══════════════════════════════════════════════════════════════════════════════
# 3. TEST OLUŞTURMA
# ══════════════════════════════════════════════════════════════════════════════

def test_olustur():
    """Test dosyaları oluştur."""
    print("\n🧪 Test Dosyaları Oluşturuluyor...")
    
    test_klasoru = PROJE_KOK / "tests" / "optimized"
    test_klasoru.mkdir(exist_ok=True)
    
    # Config testi
    config_test = test_klasoru / "test_config.py"
    with open(config_test, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""Config tutarlılığı testi."""

import yaml
from pathlib import Path

def test_config_tutarliligi():
    """Config dosyalarında tutarlılık kontrolü."""
    proje_kok = Path(__file__).parent.parent.parent
    
    config_dosya = proje_kok / "config.yaml"
    assert config_dosya.exists(), "config.yaml bulunamadı"
    
    with open(config_dosya, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    assert "general" in config
    assert "default_provider" in config["general"]
    assert config["general"]["default_provider"] == "xiaomi"
    
    print("✅ Config tutarlılığı başarılı")

def test_env_dosyalari():
    """Env dosyalarında tutarlılık kontrolü."""
    proje_kok = Path(__file__).parent.parent.parent
    env_dosya = proje_kok / ".env"
    
    assert env_dosya.exists(), ".env bulunamadı"
    
    with open(env_dosya, 'r', encoding='utf-8') as f:
        icerik = f.read()
    
    assert "XIAOMI_API_KEY=*** in icerik
    assert "ReYMeN_DEFAULT_PROVIDER=xiaomi" in icerik
    
    print("✅ Env dosyaları tutarlı")

if __name__ == "__main__":
    test_config_tutarliligi()
    test_env_dosyalari()
    print("\\n🎉 Tüm testler başarılı!")
''')
    
    # API testi
    api_test = test_klasoru / "test_api.py"
    with open(api_test, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""API bağlantısı testi."""

import os
import json
import urllib.request
from pathlib import Path

def test_xiaomi_api():
    """Xiaomi API bağlantısını test et."""
    proje_kok = Path(__file__).parent.parent.parent
    
    env_dosya = proje_kok / ".env"
    with open(env_dosya, 'r', encoding='utf-8') as f:
        for satir in f:
            if satir.startswith("XIAOMI_API_KEY=***                key = satir.split("=", 1)[1].strip()
                break
    
    assert key, "XIAOMI_API_KEY bulunamadı"
    assert len(key) > 10, "XIAOMI_API_KEY çok kısa"
    
    req = urllib.request.Request(
        "https://api.xiaomimimo.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "mimo-v2.5-pro",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }).encode()
    )
    
    resp = urllib.request.urlopen(req, timeout=15)
    assert resp.status == 200
    
    print("✅ Xiaomi API bağlantısı başarılı")

if __name__ == "__main__":
    test_xiaomi_api()
    print("\\n🎉 API testi başarılı!")
''')
    
    print(f"  ✅ Test dosyaları oluşturuldu: {test_klasoru}")

# ══════════════════════════════════════════════════════════════════════════════
# ANA FONKSİYON
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Ana fonksiyon."""
    print("=" * 60)
    print("🚀 ReYMeN Optimizasyon Scripti v2")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description="ReYMeN optimizasyon scripti")
    parser.add_argument("--all", action="store_true", help="Tüm optimizasyonları uygula")
    parser.add_argument("--tool-azalt", action="store_true", help="Tool sayısını azalt")
    parser.add_argument("--config-birlestir", action="store_true", help="Config'leri birleştir")
    parser.add_argument("--test-olustur", action="store_true", help="Test dosyaları oluştur")
    
    args = parser.parse_args()
    
    if not any([args.all, args.tool_azalt, args.config_birlestir, args.test_olustur]):
        args.all = True
    
    try:
        if args.all or args.tool_azalt:
            tool_azalt()
        
        if args.all or args.config_birlestir:
            config_birlestir()
        
        if args.all or args.test_olustur:
            test_olustur()
        
        print("\n" + "=" * 60)
        print("✅ TÜM OPTİMİZASYONLAR TAMAMLANDI")
        print("=" * 60)
        print(f"\n📁 Backup: {BACKUP_KOK}")
        print(f"\n📋 Sonraki adımlar:")
        print(f"   1. Test çalıştır: python -m pytest tests/optimized/ -v")
        print(f"   2. ReYMeN'i başlat: python main.py")
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
