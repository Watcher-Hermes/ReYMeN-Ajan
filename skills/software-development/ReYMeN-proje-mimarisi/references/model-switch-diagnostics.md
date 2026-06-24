# Model Switch Diagnostics

## Entry Point

`reymen` komutu su akisi izler:
```
reymen.bat (WindowsApps) → proje kokune cd → main.py
```

## Model Switch Flow

1. `main.py` baslatilir → `AIAgentOrchestrator()` olusur → `self.provider = RuntimeProvider(CONFIG)` (Beyin)
2. `gorkem_ekranu()` + `model_sec()` cagrilir
3. Kullanici model secer → `model_sec()` su adimlari yapar:
   - `agent.config["default_provider"] = yeni_prov` (config'i guncelle)
   - `_provider_kontrol_et()` ile provider'i test et
   - Basariliysa: `Beyin(cfg)` ile yeni Beyin olustur
   - `agent.provider = yeni_beyin` (provider'i degistir)
   - `_model_tercihini_kaydet()` ile `.ReYMeN/setup.json`'a kaydet

## Known Pitfalls

### 1. Broken Import in startup_ekrani.py
`startup_ekrani.py:model_sec()`'de:
```python
from beyin import Beyin  # CRASHES - beyin.py reymen/cereyan/ icinde
```
Dogrusu:
```python
from reymen.cereyan.beyin import Beyin
```
Eski kod sessiz `except: pass` ile coker, provider degismez.

### 2. Beyin Fallback Zinciri Yenilenmez
Beyin sadece `__init__`'te `_zincir_insa_et()` cagirir. Model degisince zincir ayni kalir.
Cozum: `provider_degistir(provider, model)` metodu ile zinciri yeniden insa et.

### 3. Cache (pyc) Sorunu
.py dosyasi degisse bile Python .pyc cache'ini kullanabilir.
Cozum: `__pycache__` klasorlerini temizle.

## Debug Komutlari

```python
# Aktif provider/model durumu
agent.provider.model_dogrula()

# Provider degistir
agent.provider.provider_degistir("deepseek", "deepseek-v4-flash")

# Beyin string gosterimi
str(agent.provider)  # "Beyin[provider=deepseek, model=deepseek-v4-flash, url=https://api.deepseek.com]"

# Fallback zinciri
agent.provider._fallback_zinciri
```

## Dogru Fallback Sirasi

1. DeepSeek (cloud, API key ile)
2. Xiaomi (cloud, API key ile)
3. LM Studio (yerel, son care)
