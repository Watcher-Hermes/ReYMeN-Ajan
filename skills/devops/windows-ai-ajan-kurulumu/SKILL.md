---
name: windows-ai-ajan-kurulumu
title: Windows AI Ajan Kurulumu
description: Windows'ta AI ajani kurulumu, LM Studio ayarlari, .bat baslatici, pip/venv yonetimi
tags: [windows, lm-studio, ai-agent, setup]
audience: user
---

# Windows AI Ajan Kurulumu

## Gerekliler
- Python 3.11+ (python.org)
- LM Studio (lmstudio.ai)

## Adimlar
1. pip install -r requirements.txt
2. LM Studio'yu ac, model yukle (dolphin3.0-llama3.1-8b), server baslat (localhost:1234)
3. .env dosyasina API anahtarlarini yaz
4. reyemen.bat start ile calistir

## Puf Noktalari
- LM Studio `system` mesaji kabul etmez → `user`'a cevir (beyin.py)
- .bat dosyasi shebang gerektirmez, direkt `python main.py` calistirir
- `***` maskeli env degerleri `startswith("***")` ile kontrol edilmeli — tam esitlik (`== "***"`) yetmez
- JSON yazma yarisi icin `FileLock` kullan
- .env dosyasi Python ile yazılmalı (PowerShell/Pipe ile tirnak sorunu)
- Provider fallback zinciri (Beyin): **DeepSeek → Xiaomi → LM Studio** (son care)
- `startup_ekrani.py` import yolu: `from reymen.cereyan.beyin import Beyin` (root'tan degil!)
- `/model` komutu `model_sec()` cagirir, `model_degistir()` yoktur (bug)
- `setup_keys.py --kontrol` ile hangi provider'larin aktif oldugunu gorebilirsin

## Startup Diagnosis Workflow (Ajan Neden Calismiyor?)
Ajan beklendigi gibi calismiyorsa (model switch ise yaramiyor, hala LM Studio'yu cagiriyor):

1. **Entry point'i bul**: PowerShell'de `where.exe <komut>` veya `(Get-Command <komut>).Source` ile hangi `.bat`/`.exe` calistigini tespit et
2. **.bat dosyasini oku**: `type C:\...\reymen.bat` ile hangi Python script'ini calistirdigini gor
3. **Python yolunu dogrula**: `python -c "import sys; print(sys.executable)"` ile dogru venv'in kullanildigini kontrol et
4. **Import zincirini kontrol et**: `startup_ekrani.py`'de `from beyin import Beyin` gibi kirik importlar olabilir — dogrusu `from reymen.cereyan.beyin import Beyin`
5. **DOT_ENV yolunu kontrol et (EN SIK SEBEP)**: `main.py`'de `DOT_ENV = Path(__file__).parent / ".env"` — bu `reymen/sistem/.env` demek. Eger o dosya yoksa `load_dotenv()` hicbir sey yuklemez, API anahtarlari bosa cikar, Beyin fallback ile direkt LM Studio'ya gecer.
   * Test: `python -c "from dotenv import load_dotenv; load_dotenv('HERHANGI_BIR_YOL'); print('OK')"`
   * Dogru yol: `Path(__file__).resolve().parent.parent.parent / ".env"` (root .env)
6. **`.env` yukleme sirasini dogrula**: `_env_anahtar()` once os.environ, sonra `~/AppData/Local/ReYMeN/.env`. Root `.env` sadece `load_dotenv()` ile yuklenir. `baslangic_kontrol.py`'daki `_env_deger()` de root `.env`'i kontrol etmeli.
7. **Model secim menusu sirasini kontrol et**: `startup_ekrani.py`'de `model_sec()` — API providerlar (DeepSeek 1., xAI 2.) ILK listelenmeli, local (LM Studio/Ollama) EN SONDA olmali.
8. **Yeni provider eklerken tum dosyalari kontrol et**: xAI eklenirken 4 dosyada guncelleme gerek: `main.py` CONFIG['providers']['xai'], `baslangic_kontrol.py` (_BULUT_ENV_MAP, _BULUT_MODELLER, _BULUT_ENV), `startup_ekrani.py` _BULUT_ENV
9. **Beyin durumunu test et**: 
   ```python
   from reymen.cereyan.beyin import Beyin
   cfg = {'default_provider': 'deepseek', ...}
   b = Beyin(cfg)
   d = b.model_dogrula()  # model_dogrula() metodu varsa
   print(d['aktif_provider'], d['base_url'])
   ```
10. **Fallback zincirini dogrula**: `model_dogrula()` ciktisinda LM Studio varsa ve istenmiyorsa, `_zincir_insa_et()`'i kontrol et

## Kullanici Tercihleri (Unutmaman Gerekenler)
- `sorma`: karar gerekiyorsa en mantikli secenegi kendin sec, uygula, sonra haber ver
- `bekleme`: isi background'da baslat, hemen cevap ver
- `arkada calissin`: terminal(background=true, notify_on_complete=true) kullan
- detayli analiz yap: yuzeysel grep yerine satir satir oku, import zincirini kontrol et
- XRAY protocolu uygula: once dosya yapisi, sonra import zinciri, sonra runtime test
