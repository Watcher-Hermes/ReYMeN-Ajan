# ReYMeN Projesi — Kapsamlı 5N1K Analiz ve Tamamlama Görevi

## 🎯 GÖREV TANIMI

**ReYMeN** (C:\Users\marko\Desktop\Reymen Proje\hermes_projesi) projesini baştan sona analiz et, tüm modüller arası bağlantıları haritalandır, iş akışını doğrula ve eksikleri tamamla.

---

## 1. KİM? (Proje Sahibi ve Kullanıcılar)

| Öğe | Değer |
|:----|:------|
| **Proje sahibi** | Marko (Watcher-Hermes) |
| **Kullanıcı profili** | Windows developer, Türkçe konuşan, kısa/direkt komutlar |
| **Botlar** | @Kiral38bot (Telegram), @Pasa_38_bot (ayrı sistem), ReYMeN CLI |
| **Çalışma ortamı** | Windows 10, PowerShell, Git Bash |
| **LLM Sağlayıcıları** | Xiaomi MiMo-V2.5 Pro (birincil), DeepSeek V4 Flash (fallback), LM Studio (yerel) |

---

## 2. NE? (Proje Kapsamı)

### 2.1 Mimari Özet

```
hermes_projesi/
├── main.py                    (18 satır — entry point, runpy ile reymen/sistem/main.py çağırır)
├── config.yaml                (proje config — provider, model, toolsets)
├── .env                       (API key'ler, ortam değişkenleri)
│
├── reymen/                    (ANA PAKET)
│   ├── cereyan/               (Beyin + Motor + Döngü)
│   │   ├── beyin.py           (1350 satır — LLM bağlantı katmanı, fallback zinciri)
│   │   ├── motor.py           (1535 satır — Eylem çözümleyici, tool registry)
│   │   ├── conversation_loop.py (ReAct döngüsü)
│   │   ├── planlayici.py      (Plan oluşturma)
│   │   ├── prompt_assembly.py (Prompt insası)
│   │   ├── closed_learning_loop.py (Kapalı öğrenme)
│   │   ├── robust_execution.py (Sağlam yürütme)
│   │   └── insan_arayuzu.py   (CLI arayüzü)
│   │
│   ├── hafiza/                (Hafıza sistemi)
│   │   ├── bounded_memory.py  (Sınırlı hafıza)
│   │   ├── context_manager.py (Context sıkıştırma)
│   │   ├── session_db.py      (Oturum veritabanı)
│   │   ├── vektorel_hafiza.py (Vektörel arama)
│   │   └── gorev_hafiza.py    (Görev sonrası hafıza)
│   │
│   ├── sistem/                (Sistem modülleri)
│   │   ├── main.py            (1621 satır — Ana ReAct döngüsü, CLI entry)
│   │   ├── baslangic_kontrol.py (Başlangıç ve ortam kontrolü)
│   │   ├── once_hafiza.py     (SQLite tabanlı hafıza)
│   │   ├── auto_recovery.py   (Otomatik kurtarma)
│   │   ├── circuit_breaker.py (Devre kesici)
│   │   └── monitoring/        (İzleme)
│   │
│   ├── arac/                  (Araç modülleri)
│   ├── ag/                    (Ağ modülleri)
│   ├── guvenlik/              (Güvenlik modülleri)
│   └── windows/               (Windows-specific)
│
├── telegram_bot/              (Telegram botu)
│   ├── ai_bot.py              (AI-powered bot)
│   ├── bot.py                 (Temel bot)
│   └── memory_agent.py        (Hafıza ajanı)
│
├── agent/                     (Hermes agent entegrasyonu)
│   ├── auxiliary_client.py    (Yardımcı model istemcisi)
│   ├── model_metadata.py     (Model metadata)
│   └── transports/           (API transportları)
│
├── tools/                     (136+ araç)
│   ├── web_tools.py
│   ├── file_operations.py
│   ├── memory_providers/
│   └── ...
│
└── skills/                    (925+ skill dosyası)
```

### 2.2 Kritik Modül Bağlantıları

| Kaynak | Hedef | Bağlantı Türü |
|:-------|:------|:--------------|
| `main.py` | `reymen/sistem/main.py` | runpy.run_path |
| `reymen/sistem/main.py` | `reymen/cereyan/beyin.py` | import Beyin |
| `reymen/sistem/main.py` | `reymen/cereyan/motor.py` | import Motor |
| `reymen/sistem/main.py` | `reymen/hafiza/*` | import (6 modül) |
| `reymen/cereyan/beyin.py` | `config.yaml` | config okuma |
| `reymen/cereyan/beyin.py` | `.env` | API key okuma |
| `reymen/cereyan/motor.py` | `tools/*` | tool registry |
| `reymen/sistem/baslangic_kontrol.py` | `config.yaml` | config override |
| `reymen/sistem/baslangic_kontrol.py` | `.env` | key kontrolü |
| `telegram_bot/ai_bot.py` | `reymen/cereyan/beyin.py` | LLM çağrısı |
| `agent/auxiliary_client.py` | `config.yaml` | model seçimi |

---

## 3. NEREDE? (Dosya Konumları ve Bağımlılıklar)

### 3.1 Config Dosyaları (Tutarsızlık Kontrolü)

| Dosya | İçerik | Öncelik |
|:------|:-------|:--------|
| `~/.hermes/config.yaml` | Hermes agent config | Yüksek |
| `hermes_projesi/config.yaml` | ReYMeN proje config | Yüksek |
| `hermes_projesi/.env` | API key'ler | Yüksek |
| `~/.hermes/.env` | Hermes根 env | Orta |
| `~/.hermes/profiles/*/env` | Profil env'leri | Orta |
| `reymen/sistem/.ReYMeN/setup.json` | Kayıtlı tercihler | Düşük |

### 3.2 Kontrol Edilecekler

- [ ] Tüm config dosyalarında `default_provider` tutarlı mı?
- [ ] Tüm config dosyalarında `default_model` tutarlı mı?
- [ ] `.env`'deki key'ler çalışıyor mu? (HTTP 200?)
- [ ] `setup.json` ile `config.yaml` çakışıyor mu?
- [ ] `baslangic_kontrol.py` hangi sırayla provider seçiyor?

---

## 4. NE ZAMAN? (İş Akışı Sırası)

### 4.1 Başlangıç Akışı

```
main.py
  └── runpy.run_path("reymen/sistem/main.py")
        ├── .env yükle (deepseek_key, xiaomi_key)
        ├── config.yaml yükle
        ├── import modüller (beyin, motor, hafiza, planlayici...)
        │     └── Import sırasında ~50 modül yüklenir ← YAVAŞLIK KAYNAĞI
        ├── baslangic_kontrolu(config)
        │     ├── setup.json oku → tercih provider
        │     ├── API key var mı? → DeepSeek/Xiaomi
        │     ├── LM Studio açık mı?
        │     └── Ollama var mı?
        ├── AIAgentOrchestrator(config)
        ├── startup_ekrani() → model_sec()
        ├── Telegram gateway başlat (arka plan)
        └── while True: input("ReYMeN > ")
```

### 4.2 Mesaj İşleme Akışı

```
Kullanıcı mesajı
  └── AIAgentOrchestrator
        ├── Prompt assembly (SOUL.md + MEMORY + skills)
        ├── beyin.dusun(sistem_prompt, mesajlar)
        │     ├── _zincir_insa_et() → fallback listesi
        │     ├── _kesintibilir_cagir(adim)
        │     │     ├── _cagir_ile_retry(adim)
        │     │     │     ├── _cagir(adim) → provider dispatch
        │     │     │     │     ├── xiaomi → _cagir_openai_uyumlu()
        │     │     │     │     ├── deepseek → _cagir_openai_uyumlu()
        │     │     │     │     └── lmstudio → _cagir_lmstudio()
        │     │     │     └── 401/402/429 → fallback
        │     │     └── timeout kontrol
        │     └── sonuc döndür
        ├── motor.coz(metin) → tool çağrısı
        │     ├── regex ile "Eylem: ARAÇ(...)" yakala
        │     ├── tool_registry.ara(adi)
        │     └── tool.calistir(parametreler)
        ├── iteration_budget kontrol
        ├── hafiza güncelle
        └── yanıt döndür
```

---

## 5. NEDEN? (Sorun Analizi — PowerShell Neden Yavaş?)

### 5.1 Tespit Edilen Sorunlar

| # | Sorun | Etki | Öncelik |
|:-:|:------|:-----|:--------|
| 1 | **64 tool yükleniyor** her turda | Token overhead, yavaş init | Yüksek |
| 2 | **~50 import** başında yükleniyor | 3-5sn gecikme | Yüksek |
| 3 | **Context compression** her turda çalışıyor | Ek CPU | Orta |
| 4 | **Prompt assembly** karmaşık | Token israfı | Orta |
| 5 | **Circuit breaker** ve **auto_recovery** sürekli çalışıyor | Overhead | Düşük |
| 6 | **Telegram botu hafif** — sadece polling + API | Hızlı | Referans |

### 5.2 Karşılaştırma

| Özellik | ReYMeN CLI | Telegram Bot |
|:--------|:-----------|:-------------|
| Tool sayısı | 64 | 0 (sadece API) |
| Import sayısı | ~50 | ~5 |
| Startup kontrolleri | 6+ | 0 |
| Hafıza sistemi | 5 katman | Basit JSON |
| Config karmaşıklığı | 6 dosya | 1 dosya |
| **Sonuç** | **Yavaş** | **Hızlı** |

---

## 6. NASIL? (Tamamlama Görevleri)

### A. Konfigürasyon Tutarlılığı (1. Öncelik)

```bash
# Tüm .env dosyalarını tara
find ~/.hermes -name ".env" -exec grep -l "DEEPSEEK\|XIAOMI" {} \;

# Config tutarlılığını kontrol et
python -c "
import yaml
with open('config.yaml') as f: cfg = yaml.safe_load(f)
print(f'Provider: {cfg[\"general\"][\"default_provider\"]}')
print(f'Model: {cfg[\"general\"][\"default_model\"]}')
"
```

**Yapılacaklar:**
1. Tüm config dosyalarında provider/model tutarlılığını sağla
2. `.env`'deki key'leri test et (HTTP 200?)
3. `setup.json` ile `config.yaml` çakışmasını çöz
4. `baslangic_kontrol.py` öncelik sırasını doğrula

### B. Performans İyileştirmesi (2. Öncelik)

**Yapılacaklar:**
1. **Lazy import** — modülleri ihtiyaç anında yükle
2. **Tool sayısını azalt** — sadece aktif tool'ları yükle
3. **Startup kontrollerini basitleştir** — sadece kritik olanları yap
4. **Context compression'ı opsiyonel yap** — gerekirse devre dışı bırak

### C. Eksik Modüller (3. Öncelik)

**Kontrol listesi:**
- [ ] `reymen/cereyan/motor.py` — tüm tool'lar tanımlı mı?
- [ ] `reymen/sistem/once_hafiza.py` — SQLite DB çalışıyor mu?
- [ ] `reymen/hafiza/vektorel_hafiza.py` — vektörel arama çalışıyor mu?
- [ ] `telegram_bot/ai_bot.py` — Xiaomi modelini destekliyor mu?
- [ ] `agent/auxiliary_client.py` — model geçişi çalışıyor mu?

### D. Test ve Doğrulama (4. Öncelik)

```bash
# 1. Import testi
python -c "from reymen.cereyan.beyin import Beyin; print('OK')"

# 2. Config testi
python -c "
import yaml
cfg = yaml.safe_load(open('config.yaml'))
assert cfg['general']['default_provider'] == 'xiaomi'
print('Config OK')
"

# 3. API testi
curl -s https://api.xiaomimimo.com/v1/models -H "Authorization: Bearer $XIAOMI_API_KEY" | python -m json.tool

# 4. CLI testi
echo "Merhaba" | python main.py
```

---

## 📋 ÇIKTI BEKLENTİLERİ

1. **Mimari Harita** — Tüm modüller arası bağlantılar (Mermaid diagram)
2. **Sorun Listesi** — Öncelik sıralı eksikler ve hatalar
3. **Düzeltme Planı** — Adım adım yapılacaklar
4. **Test Sonuçları** — Her modül için test raporu
5. **Performans Raporu** — Başlangıç süresi, bellek kullanımı

---

## ⚠️ KRİTİK KURALLAR

- **Geri dönüşü olmayan değişiklik yapma** — önce backup al
- **Config dosyalarını elle değiştirme** — script kullan
- **API key'leri loglama** — hassas veri
- **Test etmeden deploy etme** — her değişiklik sonrası test

---

**Proje Yolu:** `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi`
**Başlangıç:** `python main.py`
**Test:** `python -m pytest tests/ -v`
