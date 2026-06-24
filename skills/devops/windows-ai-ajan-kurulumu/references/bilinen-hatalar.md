---
skill_id: 2b91e26a1308
usage_count: 2
last_used: 2026-06-24
---
# Bilinen Hatalar ve Cozumleri (ReYMeN Projesi)

## `Model switch calismiyor — DeepSeek secince hala LM Studio'yu cagiriyor`

**Sebep**: `startup_ekrani.py` satir 412'de `from beyin import Beyin` yaziyor ama `beyin.py` `reymen/cereyan/` klasorunde, proje kokunde degil. Import sessizce cokuyor (except pass), yeni Beyin olusmuyor, eski LM Studio provider'i kalıyor.

**Cozum**: Import yolunu duzelt:
```python
# YANLIS (startup_ekrani.py):
from beyin import Beyin
agent.provider = Beyin(cfg)

# DOGRU:
from reymen.cereyan.beyin import Beyin
yeni = Beyin(cfg)
if hasattr(yeni, 'provider_degistir'):
    yeni.provider_degistir(yeni_prov, yeni_mod)
agent.provider = yeni
```

## `Acilista hala LM Studio / llava modeli geliyor`

**Sebep 1 — DOT_ENV yanlis yola bakiyor (%90)**: `main.py` satir 27'de `DOT_ENV = Path(__file__).parent / ".env"` = `reymen/sistem/.env`. Bu dosya **YOK**. `load_dotenv()` hicbir sey yuklemez, API anahtarlari bos gelir, Beyin fallback ile LM Studio'ya gecer.

**Cozum**: DOT_ENV'i root `.env`'e yonelt:
```python
# YANLIS (main.py:27):
DOT_ENV = Path(__file__).parent / ".env"

# DOGRU:
_PROJE_KOK_ENV = Path(__file__).resolve().parent.parent.parent / ".env"
if _PROJE_KOK_ENV.exists():
    load_dotenv(_PROJE_KOK_ENV, override=True)
    DOT_ENV = _PROJE_KOK_ENV
```

**Sebep 2 — Model menusu siralamasi**: `startup_ekrani.py`'de `model_sec()` LM Studio modellerini API providerlardan ONCE listeliyorsa, kullanici menude local modeli ilk gorur. Ayrica `os.environ.get()` ile env kontrol ediyor — eger `.env` yuklenmemisse hicbir API provider gosterilmez.

**Cozum**: Siralamayi degistir — API providerlar (DeepSeek, xAI, ...) ILK, local (LM Studio, Ollama) EN SON. Ayrica `_BULUT_ENV`'nin `os.environ` yaninda root `.env`'i da kontrol etmesini sagla.

**Tani testi**:
```bash
cd hermes_projesi
python -c "
from dotenv import load_dotenv
from pathlib import Path
load_dotenv('reymen/sistem/.env', override=True)
import os
print('DEEPSEEK_API_KEY:', bool(os.environ.get('DEEPSEEK_API_KEY','')))
print('Bu False donerse DOT_ENV yanlis yola bakiyor')
"
```

## `/model komutu NameError: name 'model_degistir' is not defined`

**Sebep**: `main.py` satir 1496'da `model_degistir(agent)` cagriliyor ama bu fonksiyon hicbir yerde tanimli degil. `startup_ekrani.py` sadece `model_sec` export ediyor.

**Cozum**: Cagriyi duzelt:
```python
# YANLIS (main.py):
model_degistir(agent)

# DOGRU:
from startup_ekrani import model_sec
model_sec(agent)
# Model bilgisini goster:
if hasattr(agent, 'provider') and hasattr(agent.provider, 'model_dogrula'):
    durum = agent.provider.model_dogrula()
    print(f"{durum['aktif_provider']} / {durum['aktif_model']}")
```

## `Beyin fallback zinciri hala LM Studio'yu deniyor`

**Sebep**: Beyin `__init__`'te fallback zincirini bir kere kurar, model switch sonrasi yeniden insa etmez. Ayrica `_zincir_insa_et()` diktaki provider sirasina gore ekler, oncelik siralamasi yapmaz.

**Cozum**: `beyin.py`'ye `provider_degistir()` metodu ekle:
```python
def provider_degistir(self, provider, model=None):
    self.provider = provider
    self.base_url, self.api_key = self._saglayici_baglantisi_kur(provider)
    self.model = model or self._varsayilan_model(provider)
    self._fallback_zinciri = self._zincir_insa_et()  # YENIDEN INSA ET!
    return {"basarili": True, "provider": self.provider, ...}
```

Ve `_zincir_insa_et()`'te oncelik siralamasi:
```python
# 1. Ana provider (deepseek)
# 2. Xiaomi (tercihli cloud)
# 3. Diger cloud provider'lar
# 4. LM Studio (son care, her zaman calisir)
```

## `Beyin default provider'i lmstudio, degismiyor`

**Sebep**: `main.py` CONFIG dict'inde `default_provider: "lmstudio"` yaziyor, env override edilmemisse bu kullanilir.

**Cozum**: Varsayilani deepseek yap:
```python
CONFIG = {
    "default_model": "deepseek-v4-flash",
    "default_provider": "deepseek",
    ...
}
```
Veya `.env`'de `ReYMeN_DEFAULT_PROVIDER=deepseek` ile override et.

---

## `AttributeError: 'AIAgentOrchestrator' object has no attribute 'learning'`

**Sebep**: `__init__`'te self.learning = ClosedLearningLoop() satiri,
PromptAssemblyEngine icinde kullanildiktan SONRA tanimlanmis.

**Cozum**: Attribute tanimini kullanimdan onceye al.
```python
# YANLIS:
self.prompt_engine = PromptAssemblyEngine(learning_loop=self.learning)
self.learning = ClosedLearningLoop()

# DOGRU:
self.learning = ClosedLearningLoop()
self.prompt_engine = PromptAssemblyEngine(learning_loop=self.learning)
```

---

## `LM Studio 400 Bad Request: "Only user and assistant roles are supported"`

**Sebep**: LM Studio, llava modelinde system rolunu kabul etmez.

**Cozum**: system mesajini user mesajina cevir:
```python
cevrilmis_mesajlar = []
if sistem_prompt:
    cevrilmis_mesajlar.append({"role": "user", "content": "[SISTEM]: " + sistem_prompt})
for m in mesajlar:
    if m["role"] == "system":
        cevrilmis_mesajlar.append({"role": "user", "content": "[SISTEM]: " + m["content"]})
    else:
        cevrilmis_mesajlar.append(m)
```

---

## `.env'de DEE...n gibi bozuk satirlar`

**Sebep**: write_file veya pipe ile .env yazarken tirnak/karakter kaybi.

**Cozum**: .env dosyasi Python ile yazilmali:
```python
with open('.env', 'w', encoding='utf-8') as f:
    f.write('DEEPSEEK_API_KEY=...\n')
```

---

## `== "***"` ile env kontrolu yanlis negatif verir

**Sebep**: LMSTUDIO_API_KEY=*** DeepSeek... gibi degerlerde `==` eslesmez.

**Cozum**: `startswith("***")` kullan:
```python
if not deger or deger.startswith("***"):
    return varsayilan
```

---

## `xAI provider bulunamadi / calismiyor`

**Sebep**: xAI 3 ayri dosyada tanimli olmali. Birini eksik birakmak calismamasina yol acar.

**Cozum**: xAI eklerken su 4 dosyayi da guncelle:
1. `main.py` — CONFIG['providers']['xai'] = {"base_url": "https://api.x.ai", "api_key": _env_anahtar("XAI_API_KEY")}
2. `baslangic_kontrol.py` — _BULUT_ENV_MAP ("xai": "XAI_API_KEY"), _BULUT_MODELLER ("xai": [...]), _BULUT_ENV ("xai": "XAI_API_KEY")
3. `startup_ekrani.py` — _BULUT_ENV ("xai": ("XAI_API_KEY", "grok-2-1212", "xAI / Grok"))
4. `.env` — XAI_API_KEY=... satirini ekle
