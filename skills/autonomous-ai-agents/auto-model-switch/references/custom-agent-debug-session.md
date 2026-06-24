# Custom ReYMeN Ajan — Model Switch Debug Oturumu

## Keşfedilen Bug'lar

### Bug 1: startup_ekrani.py Import Hatası
**Dosya:** `proje-koku/startup_ekrani.py` (satır ~412)
**Hata:** `from beyin import Beyin`
**Sebep:** `beyin.py` `reymen/cereyan/` altında, proje kökünde değil.
**Etki:** Import sessizce çöker (except pass), Beyin yenilenmez, LM Studio'da kalır.
**Düzeltme:** `from reymen.cereyan.beyin import Beyin`

### Bug 2: main.py NameError
**Dosya:** `proje-koku/reymen/sistem/main.py` (satır ~1496)
**Hata:** `model_degistir(agent)` → NameError
**Sebep:** `model_degistir` fonksiyonu hiç tanımlanmamış. 
**Düzeltme:** `from startup_ekrani import model_sec; model_sec(agent)`

### Bug 3: Beyin Fallback Zinciri Güncellenmiyor
**Dosya:** `proje-koku/reymen/cereyan/beyin.py`
**Hata:** `_zincir_insa_et()` sadece `__init__`'te çağrılır, model değişince yeniden inşa edilmez.
**Düzeltme:** `provider_degistir()` metodu eklendi — içinde `_zincir_insa_et()` çağrılır.

### Bug 4: LM Studio Fallback Zincirine Eklenmiyor
**Hata:** `key != "not-needed"` filtresi LM Studio'yu dışarıda bırakıyordu.
**Düzeltme:** Filter kaldırıldı, LM Studio her zaman sona ekleniyor.

## Fallback Zinciri Tasarımı

```
1. DeepSeek (birincil, deepseek-v4-flash)
2. Xiaomi (tercihli cloud, mimo-v2.5)
3. LM Studio (son çare, localhost:1234)
```

## Test Kodu

```python
from reymen.cereyan.beyin import Beyin

cfg = {
    'default_provider': 'deepseek',
    'default_model': 'deepseek-v4-flash',
    'providers': {
        'lmstudio': {'base_url': 'http://localhost:1234', 'api_key': 'not-needed'},
        'deepseek': {'base_url': 'https://api.deepseek.com', 'api_key': 'sk-...'},
        'xiaomi': {'base_url': 'https://api.minimax.chat/v1', 'api_key': 'sk-...'},
    },
}

b = Beyin(cfg)
d = b.model_dogrula()
assert d['aktif_provider'] == 'deepseek'
assert d['aktif_model'] == 'deepseek-v4-flask'
assert 'lmstudio' in [f['provider'] for f in d['fallback_listesi']]
```

## Sistemi Tanıma

```bash
# Hangi Python?
which reymen
python -c "import reymen; print(reymen.__file__)"

# Hangi hermes?
which hermes
cat ~/.bashrc | grep reymen
```
