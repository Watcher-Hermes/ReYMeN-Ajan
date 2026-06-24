# 🧠 ReYMeN Agent

> **R**eal-**Y**ielding **M**emory-**E**nhanced **N**etwork Agent

Otonom çalışan, hafıza destekli, multi-provider AI ajan. Hermes Agent fork'u olarak geliştirildi.

## 🎯 Ne Yapar?

| Özellik | Açıklama |
|---------|----------|
| 🧠 **Hafıza Sistemi** | OnceHafiza DB — güven skoru (sigmoid), kaynak URL, kategori bazlı arama |
| 🔧 **64+ Araç** | Terminal, dosya, web, YouTube, Power BI, browser |
| 🤖 **Multi-Provider** | MiMo, DeepSeek, XAI, Groq, OpenRouter, LM Studio (fallback zinciri) |
| 📱 **Telegram Bot** | 3 bot profili, SOUL.md kişilik, gateway entegrasyonu |
| 🎥 **YouTube Analiz** | Video transcript → skill kazanımı, otomatik uygulama |
| 🔒 **Tor Browser** | Tor üzerinden web otomasyonu, form doldurma |
| 🖥️ **Windows Otomasyon** | Fare/klavye kontrolü, ekran görüntüsü, VS Code entegrasyonu |
| 🐧 **Cross-Platform** | Kali Linux + Windows ajan koordinasyonu |
| 📊 **Skill Sistemi** | 4400+ SKILL.md — 5N1K formatında, kategori bazlı |
| 🔄 **Cron Jobs** | Otomatik geliştirme döngüsü, drift tespiti, skill sync |

## 🏗️ Mimari

```
ReYMeN Agent
├── cereyan/          ← Ana iş mantığı
│   ├── beyin.py      ← LLM orkestrasyon + fallback zinciri
│   ├── conversation_loop.py ← Ana REPL döngüsü
│   ├── once_hafiza.py ← Hafıza okuma (12 ham fonksiyon)
│   └── skills/       ← Skill dosyaları
├── sistem/           ← Sistem modülleri
│   ├── main.py       ← AIAgentOrchestrator
│   ├── once_hafiza.py ← Class wrapper (cereyan'dan import)
│   ├── circuit_breaker.py ← Hata yakalama
│   └── monitoring/   ← Config guard, health check
├── tools/            ← Araç modülleri
│   ├── mcp_manager.py ← MCP entegrasyonu
│   └── mcp_tool.py   ← Tool Registry
├── agent/            ← Ajan altyapısı
│   └── personalities.py ← 14 kişilik modu
├── windows/          ← Windows-specific
├── skills/           ← 4400+ SKILL.md (kategorize)
├── tests/            ← pytest test suite
├── scripts/          ← Yardımcı scriptler
└── reymen_launcher.py ← Hafif REPL giriş noktası
```

## 🚀 Kurulum

### 1. Clone
```bash
git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan.git
cd ReYMeN-Ajan
```

### 2. Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
```

### 3. Bağımlılıklar
```bash
pip install -r requirements.txt
```

### 4. API Key (.env)
```bash
# .env dosyasını oluştur
# Minimum: bir LLM provider key'i gerekli
XIAOMI_API_KEY=sk-xxx        # MiMo (en ucuz: $0.036/M)
DEEPSEEK_API_KEY=sk-xxx      # DeepSeek ($0.14/M)
XAI_API_KEY=xai-xxx          # Grok ($0.30/M)
GROQ_API_KEY=gsk-xxx         # Groq (ücretsiz tier)
```

### 5. Çalıştır
```bash
# REPL modu (hafif)
python reymen_launcher.py

# Ya da PowerShell'de
reymen
```

## 💰 Provider Fiyat Karşılaştırması

| Provider | Model | Input/1M | Output/1M | Ücretsiz |
|----------|-------|----------|-----------|----------|
| **Xiaomi MiMo** | mimo-v2.5 | $0.036 | $0.144 | $3 hediye |
| **Groq** | llama-3.1-8b | $0.05 | $0.08 | 14K req/gün |
| **DeepSeek** | v4-flash | $0.14 | $0.28 | $0.5 hediye |
| **XAI** | grok-3-mini | $0.30 | $0.50 | $25 hediye |
| **LM Studio** | local | ücretsiz | ücretsiz | — |

## 🧠 Hafıza Sistemi

```
Görev gelir
  ↓
① HAFIZA KONTROL (guven > 0.8?)
  ├─ EVET → direkt döndür (0 LLM çağrısı, $0)
  └─ HAYIR → devam
② CACHE (selam/teşekkür?)
  ├─ EVET → direkt döndür
  └─ HAYIR → devam
③ LLM ÇAĞRISI (MiMo/DeepSeek)
  └─ Fallback zinciri: MiMo → DeepSeek → XAI → Groq → LMStudio
```

**Güven Skoru (Sigmoid):**
```
guven = 1 / (1 + e^(-0.5 × (başarı - hata - 1)))

İlk başarı:     0.50
3 başarı:       0.73
10 başarı:      0.99
1 başarı + 3 hata: 0.18
```

## 🔧 Araçlar

| Kategori | Araçlar |
|----------|---------|
| **Terminal** | bash/powershell komutları, process yönetimi |
| **Dosya** | oku/yaz/ara/patch |
| **Web** | sayfa çekme, arama, form doldurma |
| **YouTube** | transcript, video bilgi, analiz |
| **Browser** | Chrome/Tor otomasyonu |
| **Power BI** | DAX sorgulama, model keşfetme |
| **MCP** | Model Context Protocol entegrasyonu |
| **TTS** | Metin → ses dönüşümü |
| **Görsel** | Ekran görüntüsü, görsel analiz |

## 📱 Telegram Bot

3 bot profili desteklenir:
- `@Pasa_38_bot` — Default profili
- `@Kiral38bot` — Kiral38 profili
- `@ReYMeN_ReYMeNbot` — ReYMeN profili

Her bot kendi `.env`'si ve SOUL.md kişiliğiyle çalışır.

## 🎥 YouTube → Skill Kazanımı

```
YouTube URL gelir
  ↓
Transcript çekilir (YOUTUBE_TRANSCRIPT)
  ↓
Talimatlar çıkarılır
  ↓
Otomatik uygulanır (terminal, dosya, config)
  ↓
Skill olarak kaydedilir
```

## 🔄 Cron Jobs

| Job | Aralık | Görev |
|-----|--------|-------|
| Kendini Geliştirme | 15dk | Test yaz, fix et, commit et |
| Skill Sync | 30dk | Hermes → ReYMeN skill kopyalama |
| Drift Detector | 6s | Duplicate modül tespiti |
| Skill Index | 6s | DB'ye skill kaydı |

## 📁 Skill Sistemi

4400+ SKILL.md dosyası, 5N1K formatında:

```markdown
| 5N1K | Açıklama |
|------|----------|
| Kim | Hangi ajan/kullanıcı |
| Ne | Ne yapılacak |
| Nerede | Hangi dosya/klasör |
| Ne Zaman | Tetikleyici koşul |
| Neden | Gerekçe |
| Nasıl | Adım adım talimat |
```

## �️ Güvenlik

- `.env` dosyaları asla commit edilmez
- API key'leri `.gitignore`'da
- Circuit breaker: 3 ardışık hata → kalıcı dur
- Kredi kartı yasağı: Ödeme işlemi yapılmaz

## 📄 Lisans

MIT License

## 🤝 Katkı

1. Fork
2. Branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Pull Request

---

**ReYMeN Agent** — Otonom çalışan, hafıza destekli AI ajan 🧠
