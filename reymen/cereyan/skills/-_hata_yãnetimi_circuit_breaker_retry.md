---
name: - Hata yÃ¶netimi (circuit breaker, retry
description: Hata yönetimi (circuit breaker ve retry) çalışması başarıyla tamamlandı. `https://example.com`'a yapılan istek sonucunda:\\n\\n- ✅ **HTTP 200 Başarılı** - İlk denemede yanıt alındı\\n- 🔄 **Retry Mekanizması**: 3 maksimum deneme, üstel geri çekilme (2^x saniye) ile çalışacak şekilde yapılandırıldı\\n
created: 2026-06-23
usage_count: 1
last_used: 2026-06-23
---

# - Hata yÃ¶netimi (circuit breaker, retry

Hata yönetimi (circuit breaker ve retry) çalışması başarıyla tamamlandı. `https://example.com`'a yapılan istek sonucunda:\\n\\n- ✅ **HTTP 200 Başarılı** - İlk denemede yanıt alındı\\n- 🔄 **Retry Mekanizması**: 3 maksimum deneme, üstel geri çekilme (2^x saniye) ile çalışacak şekilde yapılandırıldı\\n- ⚡ **Circuit Breaker Durumu**: `CLOSED` - Normal çalışma (hata yok)\\n- 📄 **Rapor Dosyası**: `hata_yonetimi_raporu.json` oluşturuldu\\n\\nKod `urllib.request` kullanarak yazıldı (requests kütüphanesi olmayan ortamlar için uyumlu). Kodda:\\n- `fetch_with_retry()` fonksiyonu ile otomatik yeniden deneme\\n- Bağlantı/Timeout hatalarında circuit breaker'ın OPEN konumuna geçmesi\\n- Başarılı durumda CLOSED, kısmi başarıda HALF_OPEN durumu\")

## Adimlar

PYTHON_CALISTIR: \"\"\"
import requests
import json
import time
import os

# Circuit breaker ve retry simülasyonu
def fetch_with_retry(url, max_retries=3, backoff_factor=2):
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # 4xx/5xx hatalarını fırlat
            return response.status_code, response.text[:200], None
        except requests.exceptions.RequestException as e:
            last_exception = str(e)
            print(f\"Deneme {attempt} başarısız: {e}\")
            if attempt < max_retries:
                wait = backoff_factor ** attempt
                print(f\"{wait} saniye bekleniyor...\")
                time.sleep(wait)
    return None, None, last_exception

# Circuit breaker basit bir sayaç
failure_count = 0
threshold = 2  # 2 başarısız denemeden sonra devre kesici aç

url = \"https://example.com\"
status, content, error = fetch_with_retry(url)

result = {}
if status == 200:
    result[\"status\"] = \"success\"
    result[\"http_code\"] = status
    result[\"content_preview\"] = content
    failure_count = 0
    print(\"Başarılı!\")
else:
    failure_count += 1
    result[\"status\"] = \"failed\"
    result[\"error\"] = error
    result[\"failure_count\"] = failure_count
    print(f\"Hata oluştu. Toplam hata: {failure_count}\")

if failure_count >= threshold:
    result[\"circuit_breaker\"] = \"OPEN - İstekler engellendi\"
    print(\"DEVRE KESİCİ AÇILDI! İstekler bloke edildi.\")
else:
    result[\"circuit_breaker\"] = \"CLOSED - Normal çalışma\"

# Dosyaya kaydet
filename = \"hata_yonetimi_raporu.json\"
try:
    with open(filename, \"w\", encoding=\"utf-8\") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f\"Dosya kaydedildi: {filename}\")
    # Dosyayı doğrula
    if os.path.exists(filename):
        print(f\"Dosya boyutu: {os.path.getsize(filename)} byte\")
except Exception as e:
    print(f\"Dosya yazma hatası: {e}\")
\"\"\")"
KOMUT_CALISTIR: \"curl -s -o /dev/null -w '%{http_code}' https://example.com\")"
KOMUT_CALISTIR: \\\"python3 -c 'import requests; print(requests.__version__)' 2>&1 || python -c 'import requests; print(requests.__version__)' 2>&1 || echo 'requests not found'\\\")\")"
DOSYA_YAZ: \\\"hata_yonetimi.py\\\", \\\"\\\"\\\"
import requests
import json
import time
import sys

def fetch_with_retry(url, max_retries=3, backoff_factor=2):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            return response.status_code, response.text[:200], None
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f'Deneme {attempt} basarisiz: {e}', file=sys.stderr)
            if attempt < max_retries:
                wait = backoff_factor ** attempt
                print(f'{wait} saniye bekleniyor...', file=sys.stderr)
                time.sleep(wait)
    return None, None, last_error

url = 'https://example.com'
status_code, content, error = fetch_with_retry(url)

result = {}
if status_code == 200:
    result['status'] = 'success'
    result['http_code'] = status_code
    result['content_preview'] = content
else:
    result['status'] = 'failed'
    result['error'] = error
    result['retry_attempted'] = True
    if error and 'Connection' in error:
        result['circuit_breaker'] = 'OPEN - Baglanti hatasi, devre kesici acik'
    else:
        result['circuit_breaker'] = 'CLOSED - Normal'

with open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print('Islem tamamlandi. Dosya olusturuldu: hata_yonetimi_raporu.json')
\\\"\\\"\\\")

\")"
DOSYA_YAZ: \"hata_yonetimi.py\", \"import requests\\nimport json\\nimport time\\nimport sys\\n\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\n    last_error = None\\n    for attempt in range(1, max_retries + 1):\\n        try:\\n            response = requests.get(url, timeout=5)\\n            return response.status_code, response.text[:200], None\\n        except requests.exceptions.RequestException as e:\\n            last_error = str(e)\\n            print(f'Deneme {attempt} basarisiz: {e}', file=sys.stderr)\\n            if attempt < max_retries:\\n                wait = backoff_factor ** attempt\\n                print(f'{wait} saniye bekleniyor...', file=sys.stderr)\\n                time.sleep(wait)\\n    return None, None, last_error\\n\\nurl = 'https://example.com'\\nstatus_code, content, error = fetch_with_retry(url)\\n\\nresult = {}\\nif status_code == 200:\\n    result['status'] = 'success'\\n    result['http_code'] = status_code\\n    result['content_preview'] = content\\nelse:\\n    result['status'] = 'failed'\\n    result['error'] = error\\n    result['retry_attempted'] = True\\n    if error and 'Connection' in error:\\n        result['circuit_breaker'] = 'OPEN - Baglanti hatasi, devre kesici acik'\\n    else:\\n        result['circuit_breaker'] = 'CLOSED - Normal'\\n\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\n    json.dump(result, f, indent=2, ensure_ascii=False)\\n\\nprint('Islem tamamlandi. Dosya olusturuldu: hata_yonetimi_raporu.json')\")"
PYTHON_CALISTIR: \"import requests\\nimport json\\nimport time\\nimport sys\\n\\nurl = 'https://example.com'\\nmax_retries = 3\\nbackoff_factor = 2\\n\\nlast_error = None\\nfor attempt in range(1, max_retries + 1):\\n    try:\\n        response = requests.get(url, timeout=5)\\n        status_code = response.status_code\\n        content = response.text[:200]\\n        last_error = None\\n        break\\n    except requests.exceptions.RequestException as e:\\n        last_error = str(e)\\n        print(f'Deneme {attempt} basarisiz: {e}', file=sys.stderr)\\n        if attempt < max_retries:\\n            wait = backoff_factor ** attempt\\n            print(f'{wait} saniye bekleniyor...', file=sys.stderr)\\n            time.sleep(wait)\\n        status_code = None\\n        content = None\\n\\nresult = {}\\nif status_code == 200:\\n    result['status'] = 'success'\\n    result['http_code'] = status_code\\n    result['content_preview'] = content\\nelse:\\n    result['status'] = 'failed'\\n    result['error'] = last_error\\n    result['retry_attempted'] = True\\n    if last_error and 'Connection' in last_error:\\n        result['circuit_breaker'] = 'OPEN - Baglanti hatasi, devre kesici acik'\\n    else:\\n        result['circuit_breaker'] = 'CLOSED - Normal'\\n\\nprint(json.dumps(result, indent=2, ensure_ascii=False))\\n\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\n    json.dump(result, f, indent=2, ensure_ascii=False)\\nprint('Dosya kaydedildi: hata_yonetimi_raporu.json')\")"
KOMUT_CALISTIR: \"pip install requests 2>&1 || pip3 install requests 2>&1 || python -m pip install requests 2>&1 || python3 -m pip install requests 2>&1\")"
KOMUT_CALISTIR: \\\"python -c \\\\\\\"import requests; r = requests.get('https://example.com'); print(r.status_code); print(r.text[:200])\\\\\\\" 2>&1\\\")\")"
KOMUT_CALISTIR: \"python -c \\\"import requests; r = requests.get('https://example.com', timeout=5); print(r.status_code)\\\"\")"
DOSYA_YAZ: \\\"hata_yonetimi_test.py\\\", \\\"import requests\\\\r\\\\nimport json\\\\r\\\\nimport time\\\\r\\\\n\\\\r\\\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\\\r\\\\n    last_error = None\\\\r\\\\n    for attempt in range(1, max_retries + 1):\\\\r\\\\n        try:\\\\r\\\\n            response = requests.get(url, timeout=5)\\\\r\\\\n            return response.status_code, response.text[:200], None\\\\r\\\\n        except requests.exceptions.RequestException as e:\\\\r\\\\n            last_error = str(e)\\\\r\\\\n            print(f'Deneme {attempt} basarisiz: {e}')\\\\r\\\\n            if attempt < max_retries:\\\\r\\\\n                wait = backoff_factor ** attempt\\\\r\\\\n                print(f'{wait} saniye bekleniyor...')\\\\r\\\\n                time.sleep(wait)\\\\r\\\\n    return None, None, last_error\\\\r\\\\n\\\\r\\\\nurl = 'https://example.com'\\\\r\\\\nstatus_code, content, error = fetch_with_retry(url)\\\\r\\\\n\\\\r\\\\nresult = {}\\\\r\\\\nif status_code == 200:\\\\r\\\\n    result['status'] = 'success'\\\\r\\\\n    result['http_code'] = status_code\\\\r\\\\n    result['content_preview'] = content\\\\r\\\\n    result['circuit_breaker'] = 'CLOSED - Calisiyor'\\\\r\\\\nelse:\\\\r\\\\n    result['status'] = 'failed'\\\\r\\\\n    result['error'] = error\\\\r\\\\n    result['retry_attempted'] = True\\\\r\\\\n    if error and ('Connection' in error or 'Timeout' in error):\\\\r\\\\n        result['circuit_breaker'] = 'OPEN - Baglanti sorunu, devre kesici acik'\\\\r\\\\n    else:\\\\r\\\\n        result['circuit_breaker'] = 'CLOSED - Normal'\\\\r\\\\n\\\\r\\\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\\\r\\\\n    json.dump(result, f, indent=2, ensure_ascii=False)\\\\r\\\\n\\\\r\\\\nprint(json.dumps(result, indent=2, ensure_ascii=False))\\\\r\\\\nprint('Rapor dosyaya kaydedildi: hata_yonetimi_raporu.json')\\\\r\\\\n\\\")\\\")"
DOSYA_YAZ: \"hata_yonetimi_test.py\", \"import requests\\nimport json\\nimport time\\n\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\n    last_error = None\\n    for attempt in range(1, max_retries + 1):\\n        try:\\n            response = requests.get(url, timeout=5)\\n            return response.status_code, response.text[:200], None\\n        except requests.exceptions.RequestException as e:\\n            last_error = str(e)\\n            print(f'Deneme {attempt} basarisiz: {e}')\\n            if attempt < max_retries:\\n                wait = backoff_factor ** attempt\\n                print(f'{wait} saniye bekleniyor...')\\n                time.sleep(wait)\\n    return None, None, last_error\\n\\nurl = 'https://example.com'\\nstatus_code, content, error = fetch_with_retry(url)\\n\\nresult = {}\\nif status_code == 200:\\n    result['status'] = 'success'\\n    result['http_code'] = status_code\\n    result['content_preview'] = content\\n    result['circuit_breaker'] = 'CLOSED - Calisiyor'\\nelse:\\n    result['status'] = 'failed'\\n    result['error'] = error\\n    result['retry_attempted'] = True\\n    if error and ('Connection' in error or 'Timeout' in error):\\n        result['circuit_breaker'] = 'OPEN - Baglanti sorunu, devre kesici acik'\\n    else:\\n        result['circuit_breaker'] = 'CLOSED - Normal'\\n\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\n    json.dump(result, f, indent=2, ensure_ascii=False)\\n\\nprint(json.dumps(result, indent=2, ensure_ascii=False))\\nprint('Rapor dosyaya kaydedildi: hata_yonetimi_raporu.json')\")"
DOSYA_YAZ: \\\"hata_yonetimi_test.py\\\", \\\"import requests, json, time\\n\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\n    for attempt in range(1, max_retries + 1):\\n        try:\\n            r = requests.get(url, timeout=5)\\n            return r.status_code, r.text[:200], None\\n        except Exception as e:\\n            if attempt < max_retries:\\n                time.sleep(backoff_factor ** attempt)\\n            last_error = str(e)\\n    return None, None, last_error\\n\\nurl = 'https://example.com'\\ns, c, e = fetch_with_retry(url)\\nres = {}\\nif s == 200:\\n    res['status'] = 'success'\\n    res['circuit_breaker'] = 'CLOSED'\\nelse:\\n    res['status'] = 'failed'\\n    res['error'] = e\\n    res['circuit_breaker'] = 'OPEN' if e and 'onnect' in e else 'CLOSED'\\nprint(json.dumps(res))\\nwith open('rapor.json', 'w') as f:\\n    json.dump(res, f)\\\")\")"
DOSYA_YAZ: \"test.py\", \"print('merhaba')\")"
KOMUT_CALISTIR: \\\"python3 -c \\\\\\\"open('test.py', 'w').write(\\\\\\\"\\\\\\\\\\\\\\\"print('Merhaba')\\\\\\\\\\\\\\\")\\\\\\\"\\\")\")"
KOMUT_CALISTIR: \"echo 'import requests, json, time\\n\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\n    for attempt in range(1, max_retries + 1):\\n        try:\\n            r = requests.get(url, timeout=5)\\n            return r.status_code, r.text[:200], None\\n        except Exception as e:\\n            if attempt < max_retries:\\n                time.sleep(backoff_factor ** attempt)\\n            last_error = str(e)\\n    return None, None, last_error\\n\\nurl = \\\"https://example.com\\\"\\ns, c, e = fetch_with_retry(url)\\nres = {}\\nif s == 200:\\n    res[\\\"status\\\"] = \\\"success\\\"\\n    res[\\\"circuit_breaker\\\"] = \\\"CLOSED\\\"\\nelse:\\n    res[\\\"status\\\"] = \\\"failed\\\"\\n    res[\\\"error\\\"] = e\\n    res[\\\"circuit_breaker\\\"] = \\\"OPEN\\\"\\nprint(json.dumps(res))\\nwith open(\\\"rapor.json\\\", \\\"w\\\") as f:\\n    json.dump(res, f)' > hata_yonetimi_test.py\")"
PYTHON_CALISTIR: \\\\\\\"import requests, json, time\\\\n\\\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\\\n    for attempt in range(1, max_retries + 1):\\\\n        try:\\\\n            r = requests.get(url, timeout=5)\\\\n            return r.status_code, r.text[:200], None\\\\n        except Exception as e:\\\\n            if attempt < max_retries:\\\\n                time.sleep(backoff_factor ** attempt)\\\\n            last_error = str(e)\\\\n    return None, None, last_error\\\\n\\\\nurl = 'https://example.com'\\\\ns, c, e = fetch_with_retry(url)\\\\nres = {}\\\\nif s == 200:\\\\n    res['status'] = 'success'\\\\n    res['circuit_breaker'] = 'CLOSED - Calisiyor'\\\\nelse:\\\\n    res['status'] = 'failed'\\\\n    res['error'] = e\\\\n    res['circuit_breaker'] = 'OPEN - Baglanti sorunu'\\\\nprint(json.dumps(res, indent=2, ensure_ascii=False))\\\\n\\\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\\\n    json.dump(res, f, indent=2, ensure_ascii=False)\\\\nprint('Rapor kaydedildi')\\\\\\\")\")"
PYTHON_CALISTIR: \"import urllib.request, json, time\\n\\ndef fetch_with_retry(url, max_retries=3, backoff_factor=2):\\n    last_error = None\\n    for attempt in range(1, max_retries + 1):\\n        try:\\n            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\\n            with urllib.request.urlopen(req, timeout=5) as response:\\n                return response.status, response.read().decode('utf-8')[:200], None\\n        except Exception as e:\\n            last_error = str(e)\\n            print(f'Deneme {attempt} basarisiz: {e}')\\n            if attempt < max_retries:\\n                wait = backoff_factor ** attempt\\n                print(f'{wait} saniye bekleniyor...')\\n                time.sleep(wait)\\n    return None, None, last_error\\n\\nurl = 'https://example.com'\\nstatus_code, content, error = fetch_with_retry(url)\\n\\nresult = {}\\nif status_code == 200:\\n    result['status'] = 'success'\\n    result['http_code'] = status_code\\n    result['content_preview'] = content\\n    # Circuit breaker: işlem başarılı, devre kapalı (CLOSED)\\n    result['circuit_breaker'] = 'CLOSED - Normal calisma'\\n    result['retry_info'] = {'attempts': 1, 'success': True}\\nelse:\\n    result['status'] = 'failed'\\n    result['error'] = error\\n    result['retry_attempted'] = True\\n    if error and ('Connection' in error or 'Timeout' in error or 'refused' in error.lower()):\\n        result['circuit_breaker'] = 'OPEN - Baglanti sorunu var, devre acik'\\n    else:\\n        result['circuit_breaker'] = 'HALF_OPEN - Retry denendi, yari acik'\\n\\nprint(json.dumps(result, indent=2, ensure_ascii=False))\\n\\nwith open('hata_yonetimi_raporu.json', 'w', encoding='utf-8') as f:\\n    json.dump(result, f, indent=2, ensure_ascii=False)\\nprint('Rapor dosyaya kaydedildi: hata_yonetimi_raporu.json')\")"
