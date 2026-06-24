---
skill_id: 4b39af26867f
usage_count: 1
last_used: 2026-06-24
---
# .env Yonetimi

## Temel Kurallar
1. `.env` dosyasi Python ile yazilir (PowerShell heredoc tirnak sorunu yapar)
2. Her degisken ayri satirda, yorum ayri satirda olmali
3. `***` maskeli degerler `startswith("***")` ile kontrol edilir
4. `.env.example` asla guncel kalmaz — dogrudan `.env` kullan
5. **Root `.env` ONCE yuklenmeli**: main.py `load_dotenv()` root `.env`'den yapmali (`reymen/sistem/.env` degil).
   - Dogru yol: `Path(__file__).resolve().parent.parent.parent / ".env"`
   - Eger root `.env` yoksa: `Path(__file__).parent / ".env"` (fallback)
6. **`.env` yukleme sirasi (oncelik):** os.environ > root `.env` (load_dotenv) > ReYMeN .env (`~/AppData/Local/ReYMeN/.env`) > `baslangic_kontrol.py` _env_deger() dogrudan okuma

## Env Okuma Fonksiyonu (Standart)
```python
def _env_anahtar(anahtar, varsayilan=""):
    deger = os.environ.get(anahtar, "").strip()
    if not deger or deger.startswith("***") or deger == "...":
        # Root .env (load_dotenv ile yuklenmemisse)
        _root_env = Path(__file__).resolve().parent.parent.parent / ".env"
        if _root_env.exists():
            with open(_root_env) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{anahtar}="):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val and not val.startswith("***"):
                            os.environ[anahtar] = val
                            return val
        # ReYMeN .env (fallback)
        hermes_env = Path(r"C:\Users\marko\AppData\Local\ReYMeN\.env")
        if hermes_env.exists():
            with open(hermes_env, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{anahtar}="):
                        val = line.split("=", 1)[1].strip()
                        if val and not val.startswith("***"):
                            os.environ[anahtar] = val
                            return val
        return varsayilan
    return deger
```

## Cift Yonlu Senkronizasyon
Iki sistem ortak `.env` kullaniyorsa:
1. Once kendi .env'ni oku
2. `***` olan degerleri digerinin .env'sinden doldur
3. Kendi .env'nde olup digerinde olmayan degerleri karsiya yaz

```python
def _env_anahtar(anahtar, varsayilan=""):
    deger = os.environ.get(anahtar, "").strip()
    if not deger or deger.startswith("***") or deger == "...":
        hermes_env = Path(r"C:\Users\marko\AppData\Local\hermes\.env")
        if hermes_env.exists():
            with open(hermes_env, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{anahtar}="):
                        val = line.split("=", 1)[1].strip()
                        if val and not val.startswith("***"):
                            os.environ[anahtar] = val
                            return val
        return varsayilan
    return deger
```

## Provider Fallback Env (Guncel)
Provider zinciri sirasi: **DeepSeek (birincil) → xAI/Grok (ikincil) → Xiaomi (ucuncul) → LM Studio (son care)**

Her provider icin ayri env degiskeni:
- `DEEPSEEK_API_KEY` — DeepSeek API anahtari (BIRINCI ONCELIK)
- `XAI_API_KEY` — xAI / Grok API anahtari (IKINCI ONCELIK)
- `XIAOMI_API_KEY` — Xiaomi/MiniMax API anahtari
- `XIAOMI_BASE_URL` — Xiaomi API endpoint (varsayilan: `https://api.minimax.chat/v1`)
- `OPENAI_API_KEY` — OpenAI yedek
- `ANTHROPIC_API_KEY` — Anthropic yedek
- `GROQ_API_KEY` — Groq yedek
- `OPENROUTER_API_KEY` — OpenRouter yedek

LM Studio her zaman calisir, API anahtari gerekmez (localhost:1234).

## Yeni Provider Ekleme Kontrol Listesi
Yeni bir API provider eklerken su dosyalarin TUMUNU guncelle:
1. `main.py` — CONFIG['providers'][provider_adi] ekle, base_url + api_key ile
2. `baslangic_kontrol.py` — 3 ayri yerde:
   - `_BULUT_ENV_MAP` (setup.json okumasi icin)
   - `_BULUT_MODELLER` (/model komutu listesi icin)
   - `_BULUT_ENV` (env degisken adi eslemesi icin)
3. `startup_ekrani.py` — _BULUT_ENV (model secim menusu icin)
4. `.env` — API_KEY=*** satirini ekle
