#!/usr/bin/env python3
"""API bağlantısı testi."""

import json
import urllib.request
from pathlib import Path

def test_xiaomi_api():
    """Xiaomi API bağlantısını test et."""
    proje_kok = Path(__file__).parent.parent.parent
    
    env_dosya = proje_kok / ".env"
    key = ""
    
    with open(env_dosya, 'r', encoding='utf-8') as f:
        for satir in f:
            if satir.startswith("XIAOMI_API_KEY"):
                key = satir.split("=", 1)[1].strip()
                break
    
    assert key, "XIAOMI_API_KEY bulunamadı"
    assert len(key) > 10, "XIAOMI_API_KEY çok kısa"
    
    req = urllib.request.Request(
        "https://api.xiaomimimo.com/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + key,
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
    print("\n🎉 API testi başarılı!")
