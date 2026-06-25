Ana dizin: C:\Users\marko\Desktop\Reymen Proje\hermes_projesi · GitHub: Watcher-Hermes/ReYMeN-Ajan (private)
§
Hafıza katmanları: 1) MEMORY.md+USER.md (junction, ortak) 2) OnceHafıza SQLite (guven>0.8→LLM atla, circuit breaker 3 hata) 3) Vektörel DB memory.db (18991 FTS5, 0.04ms, %1.9) 4) decisions.md
§
Skill: ~925 dosya, 30+ kategori. references/ ~2228 dok. Konum: skills/. 5N1K ZORUNLU. Yeni skill→kategoriye kaydet, duplicate kontrol.
§
## KURALLAR
§ Cave+NoGoblins+CLARIFY YASAK+SessizOnay(3dk)+Sıralı+KONTROL(3yontem)+gateway/pytest yasak+Cronöncelistele+3test+belirsizoncehafıza+3repo+PIPELINE REDUNDANCY+DIYAGNOZ+VISUAL+DELEGATE(uzunis→background)
§
TEST DISIPLINI: Kullanici 'test etmeden tamam deme' dedi. Her fix sonrasi: ham cikti + API gercek test + menu dogrulama. Sadece '✅' yazmak yasak. Skill: reymen-provider-config
§
Xiaomi MiMo "reasoning_content" uretir — bu token'lar da ucretlendirilir. Basit sorgularda bile 5-10 reasoning token harcanabilir.
§
§ CONFIG GUARD: Hermes root .env (profile ustunde) gateway tarafindan okunur. Key degisikliginde PROJE + ROOT + PROFILE tum .env'leri guncelle. Eski key ($1.28 kayip). Cron: 23c52d1adfa3 her 15 dk. Script: ~/.hermes/scripts/config_guard.py
§
§
## PROVIDER ÖNCELİK (2026-06-24)
§
Öncelik: 1) setup.json 2) API key varsa LM Studio ATLANIR 3) LM Studio 4) Ollama.
Düzeltme: baslangic_kontrol.py API kontrolü (192) LM Studio'dan (198) ÖNCE.
Model: mimo-v2.5→mimo-v2-pro (setup.json, beyin.py, auxiliary_client.py).
Durum: DeepSeek(key var/kredi yok), Xiaomi(aktif), xAI(silindi), LM Studio(yedek).
HARICI_API_ENV'ye XIAOMI_API_KEY eklendi. Config: setup.json>env>config.yaml.
Gateway: DISARIDAN restart, icinden YAPILMAZ. .env key'leri Python ile yaz.
GitHub: Watcher-Hermes. 3 repo: ReYMeN-Ajan, hermes-skills, hermes-mouse.
§
§
Xiaomi model adı: mimo-v2.5-pro (NOT mimo-v2-pro). API: api.xiaomimimo.com. Xiaomi key 51 kr. DeepSeek key .env'de `***` olarak kayıtlı — gerçek key yok, kredi yüklenince eklenecek.
§
MODEL TERCİHİ: Xiaomi MiMo-V2.5 Pro birincil model. DeepSeek kredi bitmiş, xAI tamamen silindi (9x pahalı). Config: provider=xiaomi, model=mimo-v2.5-pro. Fallback: deepseek → lmstudio.