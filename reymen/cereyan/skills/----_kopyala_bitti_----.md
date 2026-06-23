---
name: ---- KOPYALA BITTI ----
description: GOREV_BITTI(\"Plan basariyla uygulandi. Veri.json dosyasi C:\\\\Users\\\\marko\\\\veri.json konumunda olusturuldu. Dosyada baslik, aciklama ve url alanlari bulunuyor. Dosyanin varligi ve icerigi dogrulandi.\")
created: 2026-06-23
usage_count: 1
last_used: 2026-06-23
---

# ---- KOPYALA BITTI ----

GOREV_BITTI(\"Plan basariyla uygulandi. Veri.json dosyasi C:\\\\Users\\\\marko\\\\veri.json konumunda olusturuldu. Dosyada baslik, aciklama ve url alanlari bulunuyor. Dosyanin varligi ve icerigi dogrulandi.\")

## Adimlar

PYTHON_CALISTIR: \"import requests\\nr = requests.get('https://example.com')\\nprint(r.status_code)\\nprint(r.text[:500])\")"
PYTHON_CALISTIR: \"import urllib.request\\nimport json\\n\\n# 1. Adim: GET istegi\\nurl = 'https://example.com'\\nreq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\\nwith urllib.request.urlopen(req) as response:\\n    html = response.read().decode('utf-8')\\n    print('Status:', response.getcode())\\n    print('HTML length:', len(html))\\n    print(html[:300])\")"
PYTHON_CALISTIR: \"try:\\n    from bs4 import BeautifulSoup\\n    print('BeautifulSoup var')\\nexcept ImportError:\\n    print('BeautifulSoup yok')\")"
PYTHON_CALISTIR: \\\"import urllib.request\\\\nimport json\\\\nimport re\\\\n\\\\n# 1. HTML'yi al\\\\nurl = 'https://example.com'\\\\nreq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\\\\nwith urllib.request.urlopen(req) as response:\\\\n    html = response.read().decode('utf-8')\\\\n\\\\n# 2. Veriyi ayikla (BeautifulSoup yok, regex ile)\\\\ntitle_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)\\\\ntitle = title_match.group(1) if title_match else ''\\\\n\\\\n# Paragraf/description icin: <div> icindeki metin\\\\ndiv_match = re.search(r'<div>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)\\\\ndiv_text = div_match.group(1).strip() if div_match else ''\\\\n\\\\n# Sonuc sozlugu\\\\nveri = {\\\\n    \\\\\\\"baslik\\\\\\\": title,\\\\n    \\\\\\\"aciklama\\\\\\\": div_text,\\\\n    \\\\\\\"url\\\\\\\": url\\\\n}\\\\n\\\\n# 3. JSON dosyasina yaz\\\\nwith open('veri.json', 'w', encoding='utf-8') as f:\\\\n    json.dump(veri, f, ensure_ascii=False, indent=2)\\\\n\\\\nprint('Veri.json dosyasi olusturuldu')\\\\nprint(json.dumps(veri, ensure_ascii=False, indent=2))\\\\n\\\\n# 4. Dogrula\\\\nimport os\\\\nif os.path.exists('veri.json'):\\\\n    print('Dosya basariyla olusturuldu:', os.path.abspath('veri.json'))\\\\nelse:\\\\n    print('HATA: Dosya bulunamadi!')\\\")\")"
PYTHON_CALISTIR: \"import urllib.request\\nimport json\\nimport re\\nimport os\\n\\nurl = 'https://example.com'\\nreq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})\\nwith urllib.request.urlopen(req) as response:\\n    html = response.read().decode('utf-8')\\n\\ntitle_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)\\ntitle = title_match.group(1) if title_match else ''\\n\\ndiv_match = re.search(r'<div>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)\\ndiv_text = div_match.group(1).strip() if div_match else ''\\n\\nveri = {\\n    'baslik': title,\\n    'aciklama': div_text,\\n    'url': url\\n}\\n\\nwith open('veri.json', 'w', encoding='utf-8') as f:\\n    json.dump(veri, f, ensure_ascii=False, indent=2)\\n\\nprint('Veri.json dosyasi olusturuldu')\\nprint(json.dumps(veri, ensure_ascii=False, indent=2))\\n\\nif os.path.exists('veri.json'):\\n    print('Dosya basariyla olusturuldu:', os.path.abspath('veri.json'))\\nelse:\\n    print('HATA: Dosya bulunamadi!')\")"
