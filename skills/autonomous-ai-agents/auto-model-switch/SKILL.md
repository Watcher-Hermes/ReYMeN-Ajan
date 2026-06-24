---
name: auto-model-switch
description: ReYMeN CLI agent + custom Beyin sistemi üzerinden model sağlayıcı değiştirme. Hermes config set model, startup_ekrani model_sec, Beyin fallback zinciri.
title: "Auto Model Switch"
audience: user
tags: [agents, ai, automation, model]
category: autonomous-ai-agents
---

# Otonom Model Geçişi

## Amaç
Kullanıcıya onay sormadan, görev gerektirdiğinde otomatik model geçişi yapmak.
Fallback sırası: **DeepSeek → Xiaomi → LM Studio**

---

## Bölüm 1: Hermes CLI Model Değiştirme

### CLI agent'dan model değiştirme (ÖNERİLEN)
```bash
hermes config set model <alias>
```
Alias'lar (config.yaml'dan okunur): `deepseek`, `dolphin`, `dolphin-lmstudio`, `llama`
**NOT:** Bu değişiklik sadece **yeni oturumlarda** geçerlidir.

### Manuel interaktif model değiştirme
```bash
hermes model
```

### Config.yaml düzenleme
```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com
```

---

## Bölüm 2: Custom ReYMeN Ajan Model Değiştirme (startup_ekrani.py + Beyin)

Bu bölüm **custom ReYMeN ajan sistemi** (main.py / beyin.py / startup_ekrani.py) için geçerlidir.

### Model Seçim Menüsü

`model_sec(agent)` fonksiyonu:
1. LM Studio modellerini listeler (`http://localhost:1234/v1/models`)
2. Ollama modellerini listeler (`http://localhost:11434/api/tags`)
3. Bulut provider'ları env anahtarına göre ekler
4. Kullanıcı seçim yapar → `_provider_kontrol_et()` ile doğrulama
5. Başarılıysa yeni `Beyin` oluşturur + `provider_degistir()` çağırır

### KRİTİK: Import Hatası

```python
# ❌ ESKİ (ÇALIŞMAZ):
from beyin import Beyin  # ImportError! beyin.py reymen/cereyan/ klasöründe

# ✅ DÜZELTİLMİŞ:
from reymen.cereyan.beyin import Beyin
```

startup_ekrani.py proje KÖKÜNDE, beyin.py `reymen/cereyan/` altında.

### KRİTİK: model_degistir() Yok

`main.py`'de `/model` komutu `model_degistir(agent)` çağırıyordu ama bu fonksiyon TANIMLI DEĞİL. Doğrusu:
```python
from startup_ekrani import model_sec
model_sec(agent)
```

### Fallback Zinciri Sıralaması

| # | Provider | Ne Zaman |
|:-:|:---------|:---------|
| 1 | **DeepSeek** (birincil) | Her zaman dene |
| 2 | **Xiaomi** (tercihli cloud) | DeepSeek hata verirse |
| 3 | **Diğer cloud** (OpenRouter, OpenAI, vb.) | API key varsa |
| 4 | **LM Studio** (son çare) | Tüm cloud'lar başarısız olursa |

### provider_degistir() Metodu

Beyin'e `provider_degistir()` eklendi — fallback zincirini YENİDEN İNŞA EDER:

```python
def provider_degistir(self, provider, model=None):
    self.provider = provider
    self.base_url, self.api_key = self._saglayici_baglantisi_kur(provider)
    self.model = model or self._varsayilan_model(provider)
    self._fallback_zinciri = self._zincir_insa_et()  # ← KRİTİK
```

### Doğrulama

```python
durum = agent.provider.model_dogrula()
# → {"aktif_provider": "deepseek", "aktif_model": "deepseek-v4-flash",
#    "base_url": "https://api.deepseek.com", "fallback_listesi": [...]}
```

---

## PITFALLS

### Custom Agent (main.py / Beyin)
- **`from beyin import Beyin` çalışmaz** — doğru: `from reymen.cereyan.beyin import Beyin`
- **`model_degistir()` fonksiyonu yok** — `model_sec()` kullan
- **Yeni Beyin → fallback zinciri OTOMATİK GÜNCELLENMEZ** — `provider_degistir()` çağır
- **Config varsayılanları:** `default_provider: deepseek`, `default_model: deepseek-v4-flash`
- **Xiaomi API anahtarı:** `.env`'de `XIAOMI_API_KEY=***`
- **Xiaomi base_url:** `.env`'de `XIAOMI_BASE_URL=https://api.minimax.chat/v1`

### Genel
- **Model seçimi mevcut oturumu etkilemez** — yeni oturum gerekir (Hermes CLI)
- **Kullanıcı fark eder** — model hala eskisi gibiyse uyar
- **Hangi sistem çalışıyor?** ÖNCE kontrol et: `python -c "import reymen; print(reymen.__file__)"` veya `which reymen` ile entry point'i bul. main.py/beyin.py DEĞİŞİKLİKLERİ sadece CUSTOM sistemde geçerli.
- **Hanisilasyon önleme:** Bir dosyayı değiştirmeden ÖNCE çalışan kod tarafından GERÇEKTEN kullanıldığını doğrula. Import chain'i takip et.

## Kaynak
- ReYMeN Agent skill: `hermes-agent` (model seçimi bölümü)
- Custom agent: `reymen/cereyan/beyin.py` (Beyin sınıfı, fallback zinciri)
- Custom agent: `reymen/sistem/main.py` (CONFIG, AIAgentOrchestrator)
- Custom agent: `startup_ekrani.py` (model_sec, model seçim menüsü)
- Hermes profile: `C:\Users\marko\AppData\Local\hermes\profiles\reymen\config.yaml`
