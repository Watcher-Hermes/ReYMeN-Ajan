---
name: 1. Web'den gÃ¼ncel TÃ¼rk AI giriÅŸimleri
description: "GOREV_BITTI(\"GÖREV TAMAMLANDI

Türk AI girişimlerini başarıyla topladım ve veri.json dosyasına kaydettim.

**Yapılan İşlemler:**
1. **web_scrape.py** dosyası oluşturuldu (21 satır
created: 2026-06-23
usage_count: 1
last_used: 2026-06-23
---

# 1. Web'den gÃ¼ncel TÃ¼rk AI giriÅŸimleri

"GOREV_BITTI(\"GÖREV TAMAMLANDI

Türk AI girişimlerini başarıyla topladım ve veri.json dosyasına kaydettim.

**Yapılan İşlemler:**
1. **web_scrape.py** dosyası oluşturuldu (21 satır

## Adimlar

PYTHON_CALISTIR: \"import requests\\nurl = 'https://api.turkai.com/v1/public/openweathermap'\\ntry:\\n    r = requests.get(url, timeout=10)\\n    print('Status:', r.status_code)\\n    print('Response (ilk 500 karakter):', r.text[:500])\\nexcept Exception as e:\\n    print('Hata:', e)\")"
PYTHON_CALISTIR: \"import urllib.request, json\\nurl = 'https://api.turkai.com/v1/public/openweathermap'\\ntry:\\n    with urllib.request.urlopen(url, timeout=10) as response:\\n        data = response.read().decode('utf-8')\\n        print('Status:', response.status)\\n        print('Response (ilk 500 karakter):', data[:500])\\nexcept Exception as e:\\n    print('Hata:', str(e))\")"
KOMUT_CALISTIR: \\\"curl -s -m 10 'https://api.turkai.com/v1/public/openweathermap' 2>&1\\\")\")"
WEB_ARA: \\\"güncel Türk yapay zeka girişimleri 2025 liste\\\")\")"
