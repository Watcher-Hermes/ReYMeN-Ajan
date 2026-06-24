# ReYMeN — Claude'a Sorulacak Eksikler (2. Tur)

## Talimat
Bu dosyadaki her maddeyi sırayla kontrol et ve düzelt.
Her adımda: ❌ varsa düzelt, ✅ ise geç.
Sonunda eksik kalan varsa bu dosyayı güncelle.

---

## 1. agent/transport/ Eksik Sınıflar (Geçen Sefer Biz Ekledik — Doğrula)

- [ ] `agent/transports/codex_app_server.py` → `CodexAppServerClient` sınıfı var mı?
- [ ] `agent/transports/codex_event_projector.py` → `CodexEventProjector` sınıfı var mı?
- [ ] `python3 -c "from agent.transports import listele; print(listele())"` → 11+ transport listelemeli
- [ ] Transport import testi: `python3 -c "from agent.transports.codex_app_server import CodexAppServerClient"` çalışmalı

## 2. Kök ↔ agent/ Dosya Senkronizasyonu

Kök ve agent/ arasında **86 aynı isimli dosya** var. Hangileri güncel değil?

- [ ] `diff -q credential_pool.py agent/credential_pool.py` → fark varsa not et (sadece boyut, içerik farkı beklenir)
- [ ] `diff -q prompt_caching.py agent/prompt_caching.py` → fark varsa not et
- [ ] `diff -q conversation_loop.py agent/conversation_loop.py` → fark varsa not et
- [ ] `diff -q system_prompt.py agent/system_prompt.py` → fark varsa not et
- [ ] **ÖNEMLİ:** Kök sürüm mü yoksa agent/ sürümü mü kullanılıyor? Hangi dosyalar hangi sürümü import ediyor?

## 3. Gateway Çalışıyor mu?

- [ ] `python3 -c "import gateway; print(dir(gateway))"` → hata yok
- [ ] `gateway/telegram_platform.py` var mı? (veya benzeri)
- [ ] Telegram bot token `.env`'de var mı? (`grep TELEGRAM .env`)
- [ ] Gateway testi: `python3 -c "from gateway import run; print('OK')"`

## 4. Çalıştırma Testi

- [ ] `python3 -c "from beyin import Beyin; b = Beyin({'default_provider':'lmstudio','providers':{'lmstudio':{'base_url':'http://localhost:1234','api_key':'not-needed'}}}); print('Beyin olustu')"`
- [ ] `python3 -c "from motor import Motor; m = Motor({'default_provider':'lmstudio','providers':{'lmstudio':{'base_url':'http://localhost:1234','api_key':'not-needed'}}}); print('Motor olustu')"`
- [ ] `python3 -c "import main"` → modül olarak import edilebiliyor mu? (Not: main.py dogrudan calisir, import'ta __name__ kontrolu var mi?)

## 5. .env ve API Anahtarları

- [ ] `.env` dosyası var mı?
- [ ] Hangi API anahtarları tanımlı? (`grep -E "API_KEY|TOKEN" .env`)
- [ ] En az 1 provider çalışıyor mu? (ping testi)
- [ ] OpenRouter API key var mı? (fallback için kritik)

## 6. Test Coverage

- [ ] `python3 -m pytest tests/test_beyin.py -q` → 62 passed
- [ ] `python3 -m pytest tests/test_motor.py -q --tb=short 2>&1 | tail -3`
- [ ] `python3 -m pytest tests/ -q --tb=short 2>&1 | tail -5` → genel durum
- [ ] Kaç test var? Kaçı geçiyor? (`= X passed, Y failed, Z skipped in ...s =`)

## 7. Git Durumu

- [ ] `git status` → temiz mi? commitlenmemiş dosya var mı?
- [ ] `.gitignore`'da `__pycache__`, `.env`, `*.pyc`, `logs/` var mı?
- [ ] Varsa commit değişiklikleri: `git add -A && git commit -m "Claude fix turu + cleanup"`

## 8. ReYMeN'e Özgü Dosyaların Durumu

- [ ] `motor.py` import'ları çalışıyor mu? `python3 -m py_compile motor.py`
- [ ] `beyin.py` import'ları çalışıyor mu? `python3 -m py_compile beyin.py`
- [ ] `cli.py` import'ları çalışıyor mu? `python3 -m py_compile cli.py`
- [ ] `main.py` import'ları çalışıyor mu? `python3 -m py_compile main.py`
- [ ] `ReYMeN_state.py` var mı ve çalışıyor mu?
- [ ] `conversation_loop.py` var mı ve çalışıyor mu?
- [ ] `steering_loop.py` var mı ve çalışıyor mu?
- [ ] `sistem_talimati.py` var mı ve çalışıyor mu?
- [ ] `gorev_hafiza.py` var mı ve çalışıyor mu?

---

## Başarı Kriteri

Tüm maddeler ✅ olduğunda:
- `python3 -c "from beyin import Beyin; from motor import Motor; print('ReYMeN HAZIR')"`
- 62 beyin testi geçiyor
- Hiçbir `ModuleNotFoundError` kalmamış
- Git temiz
