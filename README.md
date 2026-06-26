# 🧠 ReYMeN Agent

> **R**eal-**Y**ielding **M**emory-**E**nhanced **N**etwork Agent
> Otonom AI asistan, hafıza destekli multi-provider ajan sistemi

![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![GitHub](https://img.shields.io/github/last-commit/Watcher-Hermes/ReYMeN-Ajan?style=flat-square)
[![Tests](https://github.com/Watcher-Hermes/ReYMeN-Ajan/actions/workflows/ci.yml/badge.svg)](https://github.com/Watcher-Hermes/ReYMeN-Ajan/actions/workflows/ci.yml)

---

## 🚀 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan.git
cd ReYMeN-Ajan

# Sanal ortam oluştur
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Bağımlılıkları kur
pip install -e ".[dev]"

# API key'lerini ayarla
cp .env.example .env
# .env dosyasını düzenle — en az bir LLM provider key'i ekle
```

## ⚙️ Kullanım

```bash
# REPL modu (hafif)
python reymen_launcher.py

# CLI
reymen --help

# Gateway (tam özellik)
python reymen/sistem/main.py
```

## 🏗️ Proje Yapısı

```
reymen-agent/
├── reymen/              # Ana uygulama
│   ├── ag/              # Ağ/ağ geçidi modülleri
│   ├── arac/            # Araçlar (terminal, dosya, web, ...)
│   ├── cereyan/         # Ana iş mantığı + skill sistemi
│   ├── guvenlik/        # Güvenlik modülleri
│   ├── hafiza/          # Hafıza sistemleri
│   ├── sistem/          # CLI, config, orkestrasyon
│   └── windows/         # Windows-spesifik
├── tests/               # Test suite
├── scripts/             # Yardımcı scriptler
├── pyproject.toml       # Proje yapılandırması
├── Dockerfile           # Konteyner dağıtımı
├── Makefile             # Build/test komutları
└── README.md
```

## 🎯 Özellikler

| Özellik | Açıklama |
|:---------|:----------|
| 🧠 **Hafıza Sistemi** | OnceHafiza DB — güven skoru, kaynak URL, kategori bazlı arama |
| 🔧 **64+ Araç** | Terminal, dosya, web, YouTube, Power BI, browser |
| 🤖 **Multi-Provider** | MiMo, DeepSeek, XAI, Groq, OpenRouter, LM Studio (fallback zinciri) |
| 📱 **Telegram Bot** | 3 bot profili, SOUL.md kişilik, gateway entegrasyonu |
| 🎥 **YouTube Analiz** | Video transcript → skill kazanımı, otomatik uygulama |
| 🔒 **Tor Browser** | Tor üzerinden web otomasyonu |
| 🖥️ **Windows Otomasyon** | Fare/klavye, ekran görüntüsü, VS Code entegrasyonu |
| 🐧 **Cross-Platform** | Kali Linux + Windows ajan koordinasyonu |
| 📊 **Skill Sistemi** | 5,600+ SKILL.md — 5N1K formatında, 36 kategoride |
| 🔄 **Cron Jobs** | Otomatik geliştirme döngüsü, drift tespiti, skill sync |

## 🧪 Test

```bash
# Tüm testler
pytest

# Coverage ile
pytest --cov=reymen --cov-report=html

# Tek dosya
pytest tests/test_beyin.py -v

# Hızlı (yavaş testleri atla)
pytest -m "not slow"
```

## 🐳 Docker

```bash
# Build
docker build -t reymen-agent .

# Run
docker run --rm -it -v .env:/app/.env:ro --name reymen reymen-agent
```

## 📄 Lisans

MIT © ReYMeN 2026 — [Detay](LICENSE)

Bu proje [Nous Research / Hermes Agent](https://github.com/NousResearch/hermes-agent) fork'udur.
