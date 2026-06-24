# ReYMeN Başlangıç ve Model Yönetimi

> Bu doküman, `python main.py` (reymen.bat) ile çalışan ReYMeN ajanının startup akışını, model seçim mekanizmasını ve sık karşılaşılan hataları belgeler.

## Başlangıç Akışı

reymen.bat → python main.py → baslangic_kontrolu() → AIAgentOrchestrator → gorkem_ekranu() → model_sec() → interaktif döngü

### 1. reymen.bat
```
cd /d "C:\Users\marko\Desktop\Reymen Proje\hermes_projesi"
python main.py %*
```
- Kullanıcı PowerShell'de `reymen` yazınca bu `.bat` çalışır
- WindowsApps yolunda bir kopyası daha var (`WindowsApps\reymen.bat`) — o da aynı projeyi işaret eder

### 2. Config Yükleme (main.py ~1350)
```python
kayitli = setup.config_yukle()  # .ReYMeN/setup.json'dan
aktif_config = kayitli or CONFIG  # CONFIG = module-level sabit
```

### 3. baslangic_kontrolu() — KRİTİK
`baslangic_kontrol.py:159` → Config'i override edebilir!
```python
# Öncelik sırası:
# 1. setup.json'da kayıtlı tercih (deepseek) + API key varsa → onu kullan, return
# 2. LM Studio çalışıyorsa → default'u LM Studio yap, return
# 3. Harici API key varsa → config olduğu gibi kalsın, return
# 4. Ollama kontrolü → kullanıcıya sor
```

**Tuzak:** setup.json'da `tercih_provider: deepseek` olsa bile, `DEEPSEEK_API_KEY` env'de yoksa ve projenin `.env`'sinde de yoksa, **LM Studio'ya atlar** (adım 2).

**Düzeltme:** `baslangic_kontrol.py` artık proje `.env`'sini de kontrol eder:
```python
_proje_env = Path(__file__).resolve().parent.parent / ".env"
if _proje_env.exists():
    for _satir in _proje_env.read_text().splitlines():
        if _satir.startswith(f"{_env_key}="):
            _key_deger = _satir.split("=", 1)[1].strip().strip("\"'")
```

### 4. AIAgentOrchestrator.__init__() (main.py ~276)
- Beyin oluşturur: `self.provider = RuntimeProvider(self.config)`
- CONFIG'de varsayılan artık `deepseek` + `deepseek-v4-flash`
- Fallback zinciri: DeepSeek → Xiaomi → LM Studio

### 5. startup_ekrani.py — Görkemli Ekran + Model Menüsü
`gorkem_ekranu()` → logo + yetenek listesi gösterir
`model_sec()` → kullanıcıya model seçimi sunar

### 6. Interaktif Döngü
`ReYMeN >` prompt'u → kullanıcı girişi → `agent.run_conversation(hedef)`

---

## Beyin (beyin.py) — Model Yönetimi

### Fallback Zinciri
```python
# Sıra: DeepSeek → Xiaomi → diğer cloud → LM Studio
# Her API çağrısında sırayla denenir
```

### provider_degistir() — Model Değiştirme
```python
beyin.provider_degistir("deepseek", "deepseek-v4-flash")
# → provider, model, base_url, api_key güncellenir
# → fallback zinciri yeniden inşa edilir
```

### model_dogrula() — Şu anki Durumu Gör
```python
durum = beyin.model_dogrula()
# {
#   "aktif_provider": "deepseek",
#   "aktif_model": "deepseek-v4-flash",
#   "base_url": "https://api.deepseek.com",
#   "fallback_listesi": [
#     {"provider": "deepseek", "model": "...", "url": "..."},
#     {"provider": "xiaomi", ...},
#     {"provider": "lmstudio", ...}
#   ]
# }
```

---

## Sık Karşılaşılan Hatalar

### Hata: "400 Client Error: localhost:1234"
**Nedeni:** Model switch çalışmamış, Beyin hala LM Studio'ya gidiyor.
**Çözüm:**
1. `startup_ekrani.py:412` — `from beyin import Beyin` import'u hatalı. Düzelt:
   ```python
   from reymen.cereyan.beyin import Beyin
   ```
2. `baslangic_kontrol.py` — LM Studio bulunca config'i override ediyor. Düzelt:
   ```python
   if config.get("default_provider", "") in ("", "lmstudio"):
       config["default_provider"] = "lmstudio"
   ```

### Hata: "Aktif Model : Llava-mistral (studio)"
**Nedeni:** `baslangic_kontrolu()` LM Studio'yu default yapmış (3. adım).
**Çözüm:** `.env`'de `DEEPSEEK_API_KEY` olduğundan emin ol, sonra `reymen`'i yeniden başlat.

### Hata: "NameError: name 'model_degistir' is not defined"
**Nedeni:** `main.py:1496` `model_degistir(agent)` çağırıyor ama fonksiyon tanımlı değil.
**Çözüm:** `from startup_ekrani import model_sec` ile değiştir.

### Hata: Karmaşıklık her zaman 5/5
**Nedeni:** `iteration_budget.py`'deki eski `analiz_et()` metodu çok agresif puanlıyor.
**Çözüm:** Yeni `analiz_et()` — kelime sayısı + ipucu bazlı gerçekçi puanlama.

---

## Model Değiştirme (Kullanıcı)

```
ReYMeN > /model
→ Menü açılır, sayı seç → Beyin yenilenir
```

**Önemli:** `/model` çalışmıyorsa `main.py`'de import'u kontrol et:
```python
if hedef.lower().startswith("/model"):
    from startup_ekrani import model_sec  # model_degistir DEĞİL
    model_sec(agent)
```

---

## Önemli Dosya Yolları

| Dosya | Görevi |
|:------|:--------|
| `reymen.bat` (proje kökü) | PowerShell'den `reymen` çalıştırınca bu çalışır |
| `reymen/sistem/main.py` | Ana giriş noktası, AIAgentOrchestrator |
| `reymen/sistem/baslangic_kontrol.py` | Startup kontrolü, config override |
| `reymen/cereyan/beyin.py` | Çoklu-provider LLM bağlantı katmanı |
| `reymen/cereyan/iteration_budget.py` | Tur bütçesi + karmaşıklık analizi |
| `startup_ekrani.py` | Logo + model seçim menüsü |
| `.ReYMeN/setup.json` | Kalıcı model tercihi kaydı |
| `.env` (proje kökü) | API anahtarları |
