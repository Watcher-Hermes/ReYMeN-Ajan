# ReYMeN Projesi — .md Dosya Envanteri
> Tarih: 2026-06-26
> Kapsam: Proje kökü + .ReYMeN/ + reymen/ + skills/ (proje-spesifik) + tests/ + Obsidian Vault

---

## 1. PROJE KÖKÜ (.md Dosyaları)

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `AGENTS.md` | 1.509 B | ReYMeN Agent bot talimatları: YouTube analiz, Power BI MCP, cevap stili (Cave modu, Türkçe, tablo formatı) | Bot'un sistem talimatı — ajanın nasıl davranacağını, hangi araçları kullanacağını tanımlar |
| `README.md` | 6.240 B | ReYMeN Agent ana dokümanı: mimari, kurulum, provider fiyatları, hafıza sistemi, Telegram bot, cron jobs, 4400+ skill sistemi | Proje README'si — yeni geliştiriciler için giriş noktası |
| `PROJE_DURUMU.md` | 5.189 B | Proje durum raporu: 11 eksik giderildi, test durumu (133/133), drift durumu, yapılan değişiklikler | Proje yöneticisi için anlık durum özeti |
| `Proje Amaçları.md` | 2.744 B | Vizyon, fiziksel yapı, provider zinciri, temel hedefler, kapsam, risk matrisi, sapma önleme | Projenin ne yapıp ne yapmayacağını tanımlar |
| `AI Guidelines.md` | 4.533 B | 13 zorunlu kural: doğrulama, hafıza-öncelikli çalışma, karar döngüsü, halüsinasyon önleme, sessiz onay vb. + akış diyagramı | AI asistanının ReYMeN'de nasıl çalışacağını belirler |
| `ai_guidelines.md` | 1.392 B | Kısa versiyon: oturum başında yapılacaklar, yeni özellik/bug akışı, kod yazma öncesi kontroller | AI asistanı için özlü çalışma yönergeleri |
| `decisions.md` | 7.603 B | Karar kaydı (#1-#36): No Goblins önceliği, YouTube video uygulama, Power BI, test import fix, hafıza yönetimi | Her önemli kararın 3 soru formatında (Ne? Neden? Alternatif?) kaydı |
| `Memory Bank.md` | 2.265 B | Değişiklik kaydı şablonu: tarih, yapılan, karar (3 soru), durum. 2026-06-25 kayıtları | Oturumlar arası devamlılık sağlar |
| `SKILL_DEDUP_RAPORU.md` | 6.949 B | Skill deduplikasyon analizi: 3 mükerrer çift, cross-dir karşılaştırma, fix adımları | skills/ içindeki tekrar eden skill'leri raporlar |
| `TASK_5N1K_REYMEN_ANALIZ.md` | 11.017 B | 5N1K formatında proje analizi: Kim, Ne, Nerede, Ne Zaman, Neden, Nasıl | Projenin baştan sona analiz dokümanı |
| `rey_man_hata_analizi.md` | 23.436 B | 5 kategoride hata analizi: veritabanı istatistikleri (54 kayıt), güven dağılımı, provider zinciri, hata kategorileri | Hafıza sistemindeki hataların derinlemesine analizi |
| `drift_report_latest.md` | 1.45 MB | Modül drift detektör raporu: 161+ uyumsuzluk, duplicate modül tespiti | Çok büyük — drift tespit çıktısı |
| `._README_steering_loop.md` | 2.086 B | 5 katmanlı ReAct sarmalayıcı: hafıza, sandbox, sistem talimatı, kancalar, talimat | Steering loop mimari tanımı |
| `.hermes_sync_log.md` | 249 B | Hermes sync log: upstream güncelleme kayıtları | Hermes upstream ile senkronizasyon kaydı |

---

## 2. .ReYMeN/ — Çekirdek Konfigürasyon

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `.ReYMeN/SOUL.md` | 3.637 B | Agent kimliği: halüsinasyon önleme kuralı (BUG/ENHANCE ayrımı), ilkeler, yetenekler (ReAct Loop, tool use) | Ajanın kişiliğini ve çalışma prensiplerini tanımlar |
| `.ReYMeN/USER.md` | 79.5 KB | Kullanıcı profili: Marko, Windows 11, LM Studio, Telegram, VS Code, GitHub hesabı | Kullanıcı hakkında tüm bilgileri içerir |
| `.ReYMeN/INDEX.md` | 2.292 B | Merkezi bilgi havuzu: klasör yapısı, proje durumu (Motor %100, Hafıza %90) | Proje dosya yapısı ve modül durum indeksi |
| `.ReYMeN/decisions.md` | 6.217 B | Geliştirme döngüsü karar kaydı (#72): Bandit güvenlik, test siklusu, syntax fix, security audit | En güncel karar logu |
| `.ReYMeN/kazanimlar.md` | 13.269 B | Kazanımlar ve öğretimler: mühendislik kararları, test fixleri, self-improvement hafıza yönetimi | Projede öğrenilen derslerin kaydı |
| `.ReYMeN/KARSILASTIRMA.md` | 3.971 B | Hermes Agent ↔ ReYMeN tool/skill/gateway sayı karşılaştırması | İki projenin özellik karşılaştırması |
| `.ReYMeN/KARSILASTIRMA_DERIN.md` | 5.585 B | Derinlemesine karşılaştırma: tool pattern, CLI, plugin farkları | Detaylı özellik karşılaştırması |
| `.ReYMeN/KARSILASTIRMA_DERIN_20260620.md` | 7.640 B | 20 Haziran tarihli derin karşılaştırma | Zaman bazlı karşılaştırma versiyonu |
| `.ReYMeN/MEMORY.md` | 908 B | Kısa hafıza özeti | COMPACT hafıza kaydı |
| `.ReYMeN/memory_taxonomy_5n1k.md` | 6.099 B | 5N1K hafıza taksonomisi | Hafıza kategorizasyon şeması |
| `.ReYMeN/oz_yansima_log.md` | 8.598 B | Öz yansıma logu: ajanın kendi kendini değerlendirme kayıtları | Self-improvement döngüsü çıktısı |
| `.ReYMeN/claude_eksikler_2_tur.md` | 3.894 B | Claude eksik listesi 2. tur | Claude entegrasyonu için eksiklik listesi |
| `.ReYMeN/hata_cozumleri.md` | 401 B | Hata çözümleri kısa not | Bilinen hatalara çözüm notu |
| `.ReYMeN/prompt_gelistirme_log.md` | 305 B | Prompt geliştirme logu | Prompt iyileştirme kaydı |
| `.ReYMeN/sistem_ekleri.md` | 206 B | Sistem ekleri notu | Sistem modül ek notları |

---

## 3. .ReYMeN/memories/ — Hafıza Dosyaları

| Dosya Kategorisi | Adet | Boyut Aralığı | Ne İşe Yarar |
|:-----------------|:----:|:-------------:|:-------------|
| `MEMORY.md` | 1 | 10.861 B | Ana hafıza dosyası — ajanın geçmiş deneyimleri, başarılı/hata kayıtları |
| `USER_PROFILI.md` | 1 | 2.956 B | Kullanıcı profili kopyası |
| `session_*.md` | ~20 | 614-17.865 B | Hermes oturum hafıza dump'ları |
| `hermes_default_*.md` | ~6 | 6.938-12.272 B | Default profil hafıza yedekleri |
| `hermes_reymen_*.md` | ~6 | 3.827-13.278 B | ReYMeN profil hafıza yedekleri |
| `hermes_session_cron_*.md` | ~5 | 3.727-7.852 B | Cron job oturum hafızaları |
| `hermes_backup_*.md` | 2 | 1.236-3.126 B | Hermes yedek hafıza kopyaları |
| `gorev_*.md` | ~500 | 518-1.434 B | Görev bazlı hafıza kayıtları (OnceHafiza'dan gelen) |
| `gorev_dedup_test_*.md` | 3 | ~844 B | Deduplikasyon test görev kayıtları |
| `gorev_hata_kes_*.md` | 3 | ~1.627 B | Hata kesme test kayıtları |
| `gorev_otomatik_ozet_*.md` | 3 | ~830 B | Otomatik özet test kayıtları |
| `gorev_bos_sonuc_*.md` | 3 | ~697 B | Boş sonuç test kayıtları |
| `gorev_gorev_hata_*.md` | 3 | ~915 B | Görev hata test kayıtları |
| `gorev_gorev_test_*.md` | 3 | ~787 B | Görev test kayıtları |
| `gorev_unittest_*.md` | 4 | 518-958 B | Unit test görev kayıtları |
| `gorev_komut_*.md` | 8 | ~789 B | Komut test kayıtları |
| `gorev_long_test_*.md` | 8 | ~753 B | Uzun test kayıtları |
| `gorev_t*_*.md` | 6 | ~812 B | Test kayıtları |
| `gorev_test_*.md` | 1 | 518 B | Test kaydı |
| `gorev_integration_test_*.md` | 1 | 874 B | Entegrasyon test kaydı |
| `gorev_karsilastirma_*.md` | 1 | 710 B | Karşılaştırma test kaydı |
| `gorev_uzun_*.md` | 3 | ~1.434 B | Uzun görev test kayıtları |
| `TEST.md` | 1 | 7 B | Boş test dosyası |

> **Not:** .ReYMeN/memories/ altında ~550+ otomatik oluşturulmuş görev hafıza dosyası bulunur.

---

## 4. reymen/ — Ana Kod Dizini

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `reymen/KAZANIMLAR.md` | 5.294 B | 21 Haziran kazanımları: Power BI MCP entegrasyonu, memory limit artırma, Obsidian skill kuralları | Oturum kazanımlarının kalıcı kaydı |
| `reymen/altin_kayitlar/20260621_063124_AutonomousAgentIntro_decisions.md` | 2.055 B | Autonomous Agent Intro karar kaydı | Altın kayıt — spesifik oturum kararları |
| `reymen/altin_kayitlar/20260621_063124_AutonomousAgentIntro_skills.md` | 3.073 B | Autonomous Agent Intro skill çıktıları | Altın kayıt — skill kazanımları |
| `reymen/altin_kayitlar/20260621_064621_DeepSeekModelSorgulama_decisions.md` | 2.753 B | DeepSeek model sorgulama karar kaydı | Altın kayıt — spesifik oturum kararları |
| `reymen/altin_kayitlar/20260621_064621_DeepSeekModelSorgulama_skills.md` | 2.859 B | DeepSeek model sorgulama skill çıktıları | Altın kayıt — skill kazanımları |
| `reymen/cereyan/.ReYMeN/backup_MEMORY.md` | 16.107 B | Yedek hafıza — VS Code kuralları, fare kontrol, GitHub, ekran görüntüsü kuralları | Eski hafıza yedeği |
| `reymen/cereyan/.ReYMeN/backup_USER.md` | 1.445 B | Yedek kullanıcı profili — skill yükleme kuralları, Allow Once, çalışma stili | Eski USER.md yedeği |
| `reymen/cereyan/.ReYMeN/oz_yansima_log.md` | 44.274 B | Öz yansıma logu (detaylı) | Self-improvement döngüsü detaylı çıktısı |
| `reymen/cereyan/.ReYMeN/hata_kodlari/HATA-0001.md` ~ `HATA-0174.md` | ~240-351 B (174 adet) | Hata kodları: import hataları, modül bulunamadı, syntax error vb. | Her biri spesifik bir hatanın kategorisi, zamanı ve durumu |
| `reymen/cereyan/skills/parcalanmis_gorev_4_adimonayrefer.md` | 52.789 B | Parçalanmış görev (4 adım) — onay referansı | Büyük skill dosyası — parçalı görev yönetimi |

---

## 5. skills/ (Proje-Spesifik)

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `skills/software-development/ReYMeN-proje-mimarisi/SKILL.md` | 25.787 B | ReYMeN proje mimarisi: 92 tool, 1.069 skill, Hermes karşılaştırması, gap analizi, porting workflow | Proje mimarisini anlatan en kapsamlı skill — ajanın proje yapısını anlaması için |
| `skills/software-development/ReYMeN-tool-patterns/SKILL.md` | 12.384 B | Tool geliştirme pattern'leri: session_search, execute_code, delegate_task, vision_tool kritik kod yapıları | Yeni tool eklerken kullanılacak referans |
| `skills/software-development/ReYMeN-web-search-tool/SKILL.md` | 3.183 B | DuckDuckGo web arama tool'u ekleme adımları: web_search_tool.py, motor.py kaydı | Web arama özelliği ekleme kılavuzu |
| `skills/devops/hermes-kurallar/SKILL.md` | 3.017 B | İzin verilen/engellenen işlemler listesi: otomatik onay kuralları, güvenlik politikası | Ajanın hangi işlemleri otonom yapabileceğini belirler |
| `skills/devops/hermes-kurallar/references/hermes-repo-hygiene.md` | 4.624 B | Repo hijyeni referansı: commit mesajı formatı, branch yönetimi, kod standartları | Git repo yönetim kuralları |

---

## 6. tests/ — Test Dizini

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `tests/ReYMeN_reference/stress/README.md` | 1.948 B | Stress/battle-test suite: concurrency, subprocess e2e, property fuzzing, benchmark testleri | Uzun süren stress testlerini çalıştırma talimatı |
| `tests/ReYMeN_reference/e2e/matrix_xsign_bootstrap/README.md` | 1.894 B | Matrix cross-signing bootstrap E2E test: Docker'da homeserver, key yayınlama, recovery path | Matrix entegrasyon E2E test talimatı |

---

## 7. Obsidian Vault — ReYMeN Notları

| Dosya Yolu | Boyut | Özet | Ne İşe Yarar |
|:-----------|:-----:|:-----|:-------------|
| `OneDrive/.../Obsidian Vault/ReYMeN/Bot Dogruluk ve Thinking İndikatoru.md` | 936 B | Bot doğruluk problemi: hızlı/uydurma cevaplar, thinking indikatörü, system prompt güncellemesi | Bot kalitesi için not |
| `OneDrive/.../Obsidian Vault/ReYMeN/Telegram Token Yenileme.md` | 749 B | Telegram token yenileme: BotFather, pyrogram, bot.py güncelleme | Token sızdığında yapılacak işlemler |
| `OneDrive/.../Obsidian Vault/ReYMeN/Telegram Webhook Entegrasyonu.md` | 2.899 B | Webhook entegrasyon adımları | Telegram webhook kurulum kılavuzu |
| `OneDrive/.../Obsidian Vault/ReYMeN/test-altyapisi-calismasi-2026-06-19.md` | 3.057 B | Test altyapısı çalışması notları | Test altyapısı için Obsidian notu |
| `OneDrive/.../Obsidian Vault/ReYMeN/ReYMeN Agent Hooks.md` | 1.101 B | Agent hooks kullanımı | Hook sistemi notu |
| `OneDrive/.../Obsidian Vault/ReYMeN/AI Agent Secenegi.md` | 999 B | AI agent seçenekleri | Farklı AI agent karşılaştırma notu |

---

## 8. .ReYMeN/skills/ (Cross-Profile Skills — Özet)

| Dosya Kategorisi | İçerik |
|:-----------------|:-------|
| `.ReYMeN/skills/software-development/` | Hermes-agent skill authoring, ReYMeN-proje-mimarisi references, fork-project-audit (16-17 Haziran referansları), debug patterns |
| `.ReYMeN/skills/windows-automation/` | Windows otomasyon skill'leri: tor-browser-arama, tam-sistem-yetkisi, mouse-klavye, env-kayit-kurallari, hafiza-temizligi |
| `.ReYMeN/skills/user-preferences/` | Hersona (AI kişilik) skill'leri: hersona, hersona-recommend-quiz |
| `.ReYMeN/skills/security/` | Güvenlik skill'leri: guvenlik-izleme-sistemi |
| `.ReYMeN/skills/security-constraints-read-first/SKILL.md` | Güvenlik kısıtlamaları — öncelikli okuma kuralı |
| `.ReYMeN/skills/ui-ux-pro-max/SKILL.md` | UI/UX pro max skill |

---

## ÖZET İSTATİSTİKLER

| Kategori | Dosya Sayısı |
|:---------|:------------:|
| **Proje Kökü .md** | 14 |
| **.ReYMeN/ çekirdek** | 15 |
| **.ReYMeN/memories/** | ~550+ |
| **reymen/ dizini** | ~180 (174 hata kodu dahil) |
| **skills/ (proje-spesifik)** | 5 |
| **tests/** | 2 |
| **Obsidian Vault/ReYMeN** | 6 |
| **.ReYMeN/skills/ altı** | ~50 |
| **TOPLAM (proje ile ilgili)** | **~820+ .md dosyası** |

> **En büyük dosyalar:** drift_report_latest.md (1.45 MB), USER.md (79.5 KB), parcalanmis_gorev_4_adimonayrefer.md (52.8 KB), oz_yansima_log.md (44.3 KB), ReYMeN-proje-mimarisi/SKILL.md (25.8 KB)

> **En kritik dosyalar:** AGENTS.md, README.md, PROJE_DURUMU.md, AI Guidelines.md, .ReYMeN/SOUL.md, .ReYMeN/decisions.md, .ReYMeN/kazanimlar.md
