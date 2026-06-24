#!/usr/bin/env python3
"""Beyin modülü testi."""

import sys
from pathlib import Path

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reymen.cereyan.beyin import Beyin


class TestBeyin:
    """Beyin modülü testleri."""

    def test_baslatma(self):
        """Beyin modülünün başlatılabildiğini doğrula."""
        config = {
            "default_provider": "xiaomi",
            "default_model": "mimo-v2.5-pro",
            "providers": {
                "xiaomi": {
                    "base_url": "https://api.xiaomimimo.com",
                    "api_key": "test-key"
                }
            }
        }
        beyin = Beyin(config)
        assert beyin.provider == "xiaomi"
        assert beyin.model == "mimo-v2.5-pro"
        print("✅ Beyin başlatma başarılı")

    def test_fallback_zinciri(self):
        """Fallback zincirinin doğru oluşturulduğunu doğrula."""
        config = {
            "default_provider": "xiaomi",
            "default_model": "mimo-v2.5-pro",
            "providers": {
                "xiaomi": {
                    "base_url": "https://api.xiaomimimo.com",
                    "api_key": "test-key"
                },
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "api_key": "test-key"
                }
            },
            "fallback_model": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
                "api_key": "test-key"
            }
        }
        beyin = Beyin(config)
        
        # Fallback zinciri en az 2 elemanlı olmalı
        assert len(beyin._fallback_zinciri) >= 2
        
        # İlk eleman birincil provider olmalı
        assert beyin._fallback_zinciri[0].provider == "xiaomi"
        
        print("✅ Fallback zinciri başarılı")

    def test_varsayilan_model(self):
        """Varsayılan model adının doğru döndüğünü doğrula."""
        config = {
            "default_provider": "xiaomi",
            "default_model": "mimo-v2.5-pro",
            "providers": {
                "xiaomi": {
                    "base_url": "https://api.xiaomimimo.com",
                    "api_key": "test-key"
                }
            }
        }
        beyin = Beyin(config)
        
        # Xiaomi varsayılan modeli
        model = beyin._varsayilan_model("xiaomi")
        assert model == "mimo-v2.5-pro"
        
        # DeepSeek varsayılan modeli
        model = beyin._varsayilan_model("deepseek")
        assert model == "deepseek-chat"
        
        print("✅ Varsayılan model başarılı")

    def test_anahtar_bul(self):
        """API anahtarı bulma mekanizmasını doğrula."""
        import os
        
        config = {
            "default_provider": "xiaomi",
            "default_model": "mimo-v2.5-pro",
            "providers": {
                "xiaomi": {
                    "base_url": "https://api.xiaomimimo.com",
                    "api_key": ""
                },
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": ""
                }
            }
        }
        beyin = Beyin(config)
        
        # lmstudio için "not-needed" dönmeli
        key = beyin._anahtar_bul("lmstudio", config["providers"]["lmstudio"])
        assert key == "not-needed"
        
        # Diğerleri için boş string veya env'den gelen değer
        key = beyin._anahtar_bul("xiaomi", config["providers"]["xiaomi"])
        # Env'de XIAOMI_API_KEY varsa o gelir, yoksa boş string
        assert isinstance(key, str)
        
        print("✅ Anahtar bulma başarılı")


if __name__ == "__main__":
    test = TestBeyin()
    test.test_baslatma()
    test.test_fallback_zinciri()
    test.test_varsayilan_model()
    test.test_anahtar_bul()
    print("\n🎉 Tüm beyin testleri başarılı!")
