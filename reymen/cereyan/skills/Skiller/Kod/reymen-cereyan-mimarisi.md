---
name: reymen-cereyan-mimarisi
title: "ReYMeN Cereyan Paket Mimarisi"
description: "reymen/cereyan/ paketinin tam dizin yapısı, dosya haritası ve mimari referansı. Tüm botlar bu skill'i kullanır — ikinci bir kopya yok."
version: 1.0.0
author: ReYMeN Agent
platforms: [windows]
tags: [cereyan, mimari, referans, dizin-yapisi]
audience: bot
---

# ReYMeN Cereyan Paket Mimarisi

> **Tek kaynak:** Bu skill `reymen/cereyan/` paketinin tek referansıdır.
> Tüm botlar (ReYMeN_ReYMeNbot, Kiral38bot) bu skill'i kullanır.
> Başka yerde kopya oluşturma — ikilik yasak.

## 📂 Dizin Yolu

```
Kök: C:\Users\marko\Desktop\Reymen Proje\hermes_projesi
Cereyan: C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\
Skills: C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\skills\
```

**Önemli:** Tüm yollarda `C:\Users\marko\` kullanılır, `~` veya `$HOME` değil.

## 📊 Cereyan Paketi — Genel Bakış

| Özellik | Değer |
|---------|-------|
| .py dosya | 55 adet |
| Toplam satır | 20,822 |
| En büyük dosya | `motor.py` (1,998 satır) |
| Gizli klasör | `.ReYMeN/` (hafıza DB, beceri kütüphanesi) |
| Alt klasörler | `skills/`, `skills_yeni/`, `.alt_ajan_gozlem/`, `.reymen_hafiza/` |

## 🗺️ Dosya Haritası (Büyükten Küçüğe)

| # | Dosya | Satır | Görevi |
|---|-------|-------|--------|
| 1 | `motor.py` | 1,998 | Tool çözümleme motoru — Registry→Plugin→Fallback zinciri |
| 2 | `conversation_loop.py` | 1,895 | Konuşma döngüsü — `coz()` ve `run_conversation()` |
| 3 | `beyin.py` | 1,387 | Çok-provider LLM bağlantı katmanı |
| 4 | `once_hafiza.py` | 1,125 | SQLite önbellek — circuit breaker |
| 5 | `closed_learning_loop.py` | 1,007 | Kapalı öğrenme döngüsü — beceri kristalleştirme |
| 6 | `alt_ajan.py` | 733 | Sub-agent yönetimi |
| 7 | `hata_siniflandirici.py` | 703 | Hata sınıflandırma |
| 8 | `yetenek_fabrikasi.py` | 672 | Yetenek fabrikası |
| 9 | `steering_loop.py` | 663 | 5 katmanlı yönlendirme döngüsü |
| 10 | `hata_cozucu.py` | 560 | Hata çözümleyici (Watchdog + Kod + Cozum) |
| 11 | `web_test_loop.py` | 470 | Web test döngüsü |
| 12 | `hook_dispatcher.py` | 442 | Async olay sistemi |
| 13 | `auto_web_search.py` | 433 | Otomatik web arama |
| 14 | `kendini_anlat.py` | 427 | Kendini anlatma modülü |
| 15 | `insan_arayuzu.py` | 388 | İnsan arayüzü (onay) |
| 16 | `robust_execution.py` | 354 | Retry + checkpoint çalıştırma |
| 17 | `akilli_yonlendirici.py` | 330 | Akıllı yönlendirici |
| 18 | `reflexion_motoru.py` | 293 | Reflexion — başarısızlık yansıması |
| 19 | `meta_prompt_optimizer.py` | 291 | Meta prompt optimizasyonu |
| 20 | `ajan_suru.py` | 291 | Ajan sürüsü |
| 21 | `oz_tutarlilik.py` | 283 | Self-Consistency |
| 22 | `beceri_kutuphanesi.py` | 277 | Beceri kütüphanesi |
| 23 | `oz_yansima.py` | 273 | Idle-time yansıma |
| 24 | `dinamik_arac_uretici.py` | 264 | Dinamik araç üretici |
| 25 | `prompt_assembly.py` | 262 | Prompt assembly |
| 26 | `mesaj_tamirci.py` | 258 | Mesaj onarım |
| 27 | `service_bridge.py` | 235 | Servis köprüsü |
| 28 | `adaptif_ogrenme.py` | 230 | Adaptif öğrenme |
| 29 | `gozlem.py` | 229 | Gözlem modülü |
| 30+ | Diğer 26 dosya | 50-225 | Yardımcı modüller |

## 🧠 .ReYMeN/ Gizli Klasörü

| Dosya | Boyut | İçerik |
|-------|-------|--------|
| `memory.db` | 8.9 MB | Vektörel hafıza (FTS5) |
| `ogrenmeler.db` | 33 MB | Öğrenme veritabanı |
| `hafiza.db` | 2.9 MB | Hafıza (SQLite) |
| `beceri_kutuphanesi.json` | 34 KB | Skill katalog |
| `karar.db` | 16 KB | Decision log |
| `oz_yansima_log.md` | 44 KB | Yansıma logları |
| `cokus_raporlari/` | — | Çöküş raporları |
| `hata_kodlari/` | — | Hata kodları |
| `scripts/` | — | Otomasyon scriptleri |
| `backup_MEMORY.md` | 16 KB | Memory yedek |
| `backup_USER.md` | 1.4 KB | User profile yedek |

## 🔗 İlişkili Skill'ler

| Skill | Klasör | İçerik |
|-------|--------|--------|
| `reymen-sistem-altyapisi` | `skills/devops/` | Lazy loader, MCP, health check, memory provider |
| `reymen-hafiza-oncelikli-akis` | `skills/reymen/` | Hafıza-öncelikli karar ağacı |
| `reymen-cereyan-mimarisi` | `skills/devops/` | **Bu skill** — cereyan dizin yapısı |

## ⚠️ Önemli Kurallar

1. **Tek kaynak:** Bu skill cereyan/ yapısının TEK referansıdır.
   > **Kullanıcı tercihi:** "İkilik olmasın" — asla başka yerde kopya oluşturma.
   > Bir yerde güncelle, diğerlerini sil.
2. **Yol formatı:** Windows mutlak yol (`C:\Users\marko\...`), asla `~/` veya `$HOME`
3. **Bot paylaşımı:** Her iki bot (`ReYMeN_ReYMeNbot`, `Kiral38bot`) aynı `skills/` klasörünü okur
4. **Güncelleme:** Yeni dosya eklenince bu skill'i de güncelle — `skill_manage(action='patch')`
5. **Büyük dosyalar:** `motor.py` (2K satır), `conversation_loop.py` (1.9K satır) en kritik modüller
