# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Standart dosyalar: pyproject.toml (hatchling), Dockerfile, Makefile
- Kapsamlı proje tarama raporu (KAPSAMLI_TARAMA_RAPORU.md)

### Changed
- `LICENSE` — Nous Research + ReYMeN ikili copyright
- `.env.example` — 94 satır, tüm env var kategorileri (LLM, Telegram, GitHub, GPU, vb.)
- `README.md` — Badge'ler + daha temiz yapı
- `pyproject.toml` — setuptools → hatchling + ruff + dev deps
- `.github/workflows/ci.yml` + `lint.yml` — mevcut çalışıyor

### Fixed
- `credential_persistence.py` — XOR key env/dinamik, except:pass → logging
- `setup.py`, `reymen_otomatik_duzeltici.py` — os.system → ctypes.SetConsoleMode
- 7 dosyada print() → logging dönüşümü (salted_gateway, telegram_bot, araclar*)

## [0.1.0] - 2026-06-19
### Added
- İlk release — Hermes Agent fork
- Gateway sistemi, CLI arayüzü
- 9 provider desteği (DeepSeek, MiMo, Groq, OpenAI, Anthropic, OpenRouter, XAI, LM Studio, Ollama)
- Telegram bot entegrasyonu (3 bot profili)
- Skill sistemi (5,600+ SKILL.md, 36 kategori)
- OnceHafiza hafıza sistemi
- YouTube video analiz + skill kazanımı
- Windows otomasyon (fare/klavye/ekran)
- 64+ araç (terminal, dosya, web, browser, Power BI)
- Tor browser entegrasyonu
- Cron job sistemi
- Çoklu ajan koordinasyonu (Kali + Windows)
