#!/usr/bin/env python3
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
    
    assert "XIAOMI_API_KEY" in icerik
    assert "ReYMeN_DEFAULT_PROVIDER=xiaomi" in icerik
    
    print("✅ Env dosyaları tutarlı")

if __name__ == "__main__":
    test_config_tutarliligi()
    test_env_dosyalari()
    print("\n🎉 Tüm testler başarılı!")
