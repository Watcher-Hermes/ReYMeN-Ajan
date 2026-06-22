# ReYMeN — Otonom Uygulama Otomasyonu Ajani (v2.0)

Kendi kendine düşünen (ReAct döngüsü), araç kullanan, hatalardan öğrenen
ve yeni beceriler kristalleştiren otonom yazılım ajanı.
ReYMeN Agent çekirdeği üzerine kurulu, Windows otomasyonunda uzmanlaşmıştır.

## Özellikler

### 🤖 Temel
- **ReAct Döngüsü**: Planla → Düşün → Eylem → Gözlemle → Öğren
- **17+ LLM Provider**: LM Studio, DeepSeek, OpenAI, Anthropic, Groq, Together, Ollama, vb.
- **105+ Araç**: Dosya, shell, Python, web, tarayıcı, ekran OCR, makro, ses, görsel
- **11 Platform**: Telegram, Discord, Signal, WhatsApp, Slack, Matrix, Email, SMS, Webhook
- **500+ Test**: 27 test dosyası, tamamı geçiyor

### 🪟 Windows Otomasyonu (ReYMeN'te Yok)
- **Tor otomasyonu**: Tor üzerinden form doldurma, login, kayıt, sipariş
- **Hata watchdog + OCR**: Hata yakala, OCR ile oku, otomatik çözüm uygula
- **Nişan/sh template**: 3 aşamalı ekran şablonu bulma (DOM → OpenCV → OCR)
- **Otonom nişan oluşturma**: DOM'dan otomatik şablon çıkarma

### 🧠 Öğrenme ve Güvenlik
- **Kapalı öğrenme döngüsü**: Hatalardan öğren, beceri kristalleştir
- **Öz yansıma/reflexion**: Kendi kendini düzeltme
- **Anayasa denetimi**: Güvenlik kuralları
- **İnsan onayı (HITL)**: Riskli işlemlerde kullanıcı onayı
- **Çöküş raporlayıcı**: Crash anında otomatik rapor

## Hızlı Başlangıç

```bash
# 1. Ortamı kur
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. .env dosyasını düzenle
notepad .env

# 3. Ollama'yı başlat (ayrı pencerede)
ollama serve

# 4. ReYMeN'i çalıştır
python main.py
```

## Güncelleme

ReYMeN Agent güncellemelerini ReYMeN'e çekmek için:

```bash
bash .ReYMeN_sync.sh --dry-run   # Ne değişeceğini göster
bash .ReYMeN_sync.sh --sync      # Güncellemeleri uygula
bash .ReYMeN_sync.sh --log       # Geçmiş senkronizasyon logu
```

## Test

```bash
# Tüm testleri çalıştır
pytest tests/ --ignore=tests/ReYMeN_reference

# Tek test dosyası
pytest tests/test_araclar.py -v
```

## Proje Yapısı

```
hermes_projesi/
├── main.py              # Ana giriş noktası
├── motor.py             # Araç motoru (105+ araç)
├── beyin.py             # Düşünme/karar modülü
├── guardrails.py        # Güvenlik/denetim
├── closed_learning_loop.py  # Kapalı öğrenme
├── hata_cozucu.py       # Hata watchdog + OCR
├── tor_otomasyonu.py    # Tor browser otomasyonu
├── araclar_nisan.py     # Nişan/sh template bulucu
├── nisan_yakala.py      # Manuel nişan yakalama
├── otonom_nisan_olusturucu.py  # Otonom nişan oluşturma
├── akilli_yonlendirici.py  # Akıllı ajan yönlendirici
├── cokus_raporlayici.py # Çöküş raporlayıcı
├── tool_registry.py     # Araç kayıt defteri
├── providers/           # 17 LLM provider
├── gateway/             # 11 platform desteği
├── tools/               # 105+ araç
├── tests/               # 500+ test
├── .ReYMeN_sync.sh      # ReYMeN güncelleme aracı
└── ReYMeN_cli/          # CLI arayüzü
```

## ReYMeN Agent Farkı

| Özellik | ReYMeN | ReYMeN |
|---------|:------:|:------:|
| Web UI | ✅ | ❌ |
| Docker | ✅ | ❌ |
| Güncelleme | Haftalık | Manuel sync |
| Tor otomasyonu | ❌ | ✅ |
| Hata watchdog | ❌ | ✅ |
| Kapalı öğrenme | ❌ | ✅ |
| İnsan onayı | ❌ | ✅ |
| Windows OCR | ❌ | ✅ |
