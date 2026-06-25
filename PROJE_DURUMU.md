# ReYMeN Proje Durumu & Amacı

> Son güncelleme: 2026-06-25 - **11 EKSİK GİDERİLDİ**
> Derlenme: canlı dosya taraması + git log + test çıktısı

---

## 📌 1. AMAÇ: ReYMeN Nedir?

**ReYMeN = Hermes Agent fork'u** — Türkçe konuşan, otonom çalışan, çoklu Telegram botu üzerinden hizmet veren bir AI ajanı.

| Özellik | Değer |
|:---------|:------|
| Köken | Hermes Agent (Nous Research) |
| Dil | Türkçe (birincil), İngilizce (yedek) |
| Platform | Windows 10 (Ana), Kali WSL (yardımcı) |
| Provider | DeepSeek v4 Flash → Xiaomi MiMo → xAI → Groq → LM Studio |
| Bot sayısı | 3 Telegram botu |
| CLI | `reyment` (PowerShell alias) + `python main.py` |

### Ne Yapar?
1. Telegram üzerinden doğal dil komutlarını alır
2. Web'den canlı veri çeker (döviz, altın, haber, hava durumu)
3. Dosya sistemi işlemleri yapar (okuma, yazma, düzenleme)
4. Hafızayı kullanır (OnceHafiza) — öğrenir, unutmaz
5. Kali VM ile koordineli çalışır (nmap tarama, güvenlik)
6. YouTube videolarını analiz eder, talimatları uygular
7. Otonom öğrenme döngüsü çalıştırır (closed_learning_loop)
8. Cron job'ları yönetir

---

## 📁 2. FİZİKSEL YAPI

(sabit — değişmedi)

---

## 🔄 3. AKIŞ (Nasıl Çalışır?)

### Ana Akış (CLI modu)
```
Kullanıcı → python main.py → reymen/sistem/main.py
    ↓
AIAgentOrchestrator.başlat()
    ↓
beyin.dinle() + konuş() (LLM çağrısı)
    ↓
motor.calistir(arac_adi, parametreler) → arac/modül
    ↓
Sonuç → kullanıcıya döndür
```

### Telegram Bot Akışı
```
Telegram mesajı → gateway (hermes -p reymen gateway start)
    ↓
telegram_bot → ai_bot.py → reymen_agent.py
    ↓
LLM + tool çağrısı → cevap
```

### Hafıza Akışı
```
Görev gelir → once_hafiza.hafizada_ara()
    ├─ Güven > 0.8 → direkt döndür (0 LLM)
    └─ Güven < 0.8 → LLM çağrısı → kaydet() → gelecekte hızlı
```

### Fallback Provider Zinciri
```
deepseek → xiaomi → xai → openrouter → groq → lmstudio
```

---

## 📊 4. MEVCUT DURUM

### Test Durumu
| Suite | Durum | Açıklama |
|:------|:-----:|:---------|
| `test_motor.py` | ✅ 133/133 | Geçiyor |
| `test_beyin.py` | ✅ | (133 içinde) |
| `test_cli.py` | ✅ | (133 içinde) |
| Syntax (222 .py) | ✅ 0 hata | `py_compile` tümü başarılı |
| Drift detektör | ✅ 0 drift | service_bridge/hook_dispatcher/once_hafiza çözüldü |

### Git Durumu
| Metrik | Değer |
|:-------|:------|
| Son commit | `123265cc` — "ciclo4: Bandit B602 fix" |
| Branch | main |
| Uzak repo | `Watcher-Hermes/ReYMeN-Ajan.git` |

### Çalışma Durumu
| Bileşen | Durum | Not |
|:--------|:-----:|:----|
| CLI (`python main.py`) | ✅ | Çalışıyor |
| reymen gateway | ✅ | PID 161132, Scheduled Task aktif |
| kiral38 gateway | ✅ | PID 214660, Scheduled Task aktif |
| YOLO mod | ✅ | 3 profilde de `approvals.mode: false` |
| AGENTS.md | ✅ | 43 satır (temiz, sadece bot talimatı) |
| OnceHafiza | ✅ | 500 gorev (budandı) |
| Hafıza dosyaları | ✅ | 1767→500 (en eski 1267 silindi) |
| _seen_errors.json | ✅ | Temizlendi |
| Backup klasörleri | ✅ | 3 adet silindi |
| reymen.bat → alias | ✅ | `reyment` PowerShell alias eklendi |
| Çift yapı drift | ✅ | service_bridge, hook_dispatcher, once_hafiza → cereyan TEK kaynak |
| Skills deduplicate | ⏳ | 3 mükerrer tespit, onay bekliyor |

---

## 🎯 5. YAPILANLAR (11 Eksik Giderildi)

| # | Eksik | Durum | Detay |
|:-:|:------|:-----:|:------|
| 1 | DeepSeek kredi | ⏳ | API test edilemedi (key mask). Kullanıcı manuel yüklemeli |
| 2 | Çift yapı drift | ✅ | service_bridge, hook_dispatcher, once_hafiza → cereyan TEK kaynak |
| 3 | Test kapsamı | ✅ | 133/133 passing + 222 .py syntax 0 hata + drift 0 |
| 4 | YOLO mod kontrol | ✅ | 3 profilde de `approvals.mode: false` |
| 5 | Hafıza budama | ✅ | 1767→500 (en eski 1267 dosya silindi) |
| 6 | AGENTS.md temizle | ✅ | 391→43 satır, gereksiz kod detayları çıkarıldı |
| 7 | reymen.bat fix | ✅ | `reyment` PowerShell alias eklendi |
| 8 | Backup klasörleri | ✅ | 3 _backup_* klasörü silindi |
| 9 | _seen_errors.json | ✅ | 50KB → boş `[]` |
| 10 | Skills deduplicate | ⏳ | 3 mükerrer tespit edildi, onay bekliyor |
| 11 | Electron/node_modules | ⏳ | 1.1GB desktop/. Onayını bekliyor (gerekli mi?) |

---

## 📝 KARAR GEÇMİŞİ

| # | Karar | Tarih | Ne? |
|:-:|:------|:-----:|:----|
| 14 | İlk hafıza güveni 0.5 | 2026-06-20 | 1.0→0.5, kademeli yükselt |
| 30 | cereyan TEK kaynak | 2026-06-24 | çift drift→cereyan tut, sistem import |
| 31 | Halüsinasyon önleme | 2026-06-25 | Web varsa LLM atla |
| 32 | Web cache TTL=300s | 2026-06-25 | 5dk TTL, $ kazancı |
| 33 | Loop breaker (6 max) | 2026-06-25 | Sınırsız döngü→6 çağrı limiti |
| 34 | AGENTS.md temizleme | 2026-06-25 | 391→43 satır, bot prompt'u temiz |
| 35 | Hafıza budama | 2026-06-25 | 1767→500 gorev |
| 36 | Çift yapı çözümü | 2026-06-25 | service_bridge, hook_dispatcher, once_hafiza fix |

---

*Son güncelleme: 2026-06-25 | Bu dosya `rey men ajanda kalıcı` talebiyle oluşturulmuştur.*
