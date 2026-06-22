# ReYMeN Memory 5N1K Taksonomisi

> **DB:** `reymen/cereyan/.ReYMeN/ogrenmeler.db` (1773 kayıt)  
> **Kolonlar:** id, hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi, son_kullanim, gecerlilik_tarihi, ne, nerede, nasil, neden, kim, kaynak_url  
> **Son güncelleme:** 2026-06-21

---

## 1. NE (What) — Konu/Kategori

| Ana Başlık | Alt Başlıklar | Açıklama |
|:-----------|:--------------|:---------|
| **🤖 AI/ML** (160) | `mlops`, `ai/training`, `ai/inference`, `ai/ecc`, `ai/skills`, `skill-*` | Yapay zeka, makine öğrenmesi, model eğitimi, MLOps |
| **🌐 Ağ** (137) | `network`, `nmap`, `netstat`, `ipconfig`, `port`, `wifi` | Ağ taraması, port yönetimi, bağlantı testleri |
| **💻 Kod** (104) | `code`, `software-development`, `python`, `git`, `test` | Yazılım geliştirme, kod yazma, versiyon kontrol |
| **🪟 Windows** (84) | `windows/terminal`, `windows/automation`, `windows/system` | Windows terminal, otomasyon, sistem komutları |
| **🎨 Yaratıcı** (84) | `creative`, `ascii`, `design`, `excalidraw`, `p5js`, `video` | Görsel tasarım, ASCII sanat, yaratıcı araçlar |
| **📺 Medya** (63) | `media`, `video`, `audio`, `voice`, `gif`, `youtube` | Medya işleme, video düzenleme, ses |
| **🧪 Test** (48) | `test`, `benchmark`, `evaluation`, `dogrulama` | Test, benchmark, performans/değerlendirme |
| **🚀 DevOps** (44) | `devops`, `backup`, `cron`, `deploy`, `git-push` | DevOps, CI/CD, yedekleme, dağıtım |
| **🔒 Güvenlik** (38) | `security`, `pentest`, `firewall`, `safety` | Güvenlik taraması, pentest, güvenlik önlemleri |
| **⚡ Verimlilik** (28) | `productivity`, `note-taking`, `obsidian`, `notion` | Verimlilik araçları, not alma |
| **🛠 DevOps** (Cont.) | `kali`, `system`, `kurulum` | Kali araçları, sistem yönetimi |
| **👤 Kullanıcı** (18) | `kullanici`, `user/preferences`, `profil` | Kullanıcı tercihleri, profil |
| **📊 Veri Bilimi** (4) | `data-science`, `jupyter` | Veri analizi, Jupyter |
| **🎮 Oyun** (4) | `gaming` | Oyun geliştirme |
| **📱 Diğer** (930) | `ecc---*`, `apple`, `frontend`, `desktop`, `personality` | Sınıflandırılamayan |

> **Not:** `ecc---*` öneki edge-case classification skill'lerini temsil eder (522 skill dosyasından gelen kayıtlar)

---

## 2. NEREDE (Where) — Platform/Konum

| Ana Başlık | Alt Başlıklar | Kullanım |
|:-----------|:--------------|:---------|
| **💻 Windows Yerel** (100) | `windows/local`, `windows/terminal`, `C:\...` | Windows terminal komutları, sistem yönetimi |
| **⚙️ Hermes Profil** (42) | `hermes/profiles/reymen`, `hermes/config` | Hermes ayarları, config, profile |
| **🐙 GitHub** (32) | `github/Watcher-Hermes`, `github/ReYMeN` | Repo yönetimi, PR, push |
| **📊 Power BI** (27) | `powerbi/mcp`, `powerbi/desktop` | Power BI MCP bağlantısı, veri modeli |
| **📝 Obsidian** (26) | `obsidian/vault`, `obsidian/notes` | Obsidian not alma, vault yönetimi |
| **🐉 Kali VM** (19) | `kali/vm`, `kali/network` | Kali sanal makine, ağ araçları |
| **💬 Telegram** (15) | `telegram/bot`, `telegram/chat` | Telegram bot, mesajlaşma |
| **🔗 Cross-Platform** (9) | `cross-platform/*` | Kali + Windows ortak çalışma |
| **🌐 Web** (8) | `web/search`, `web/extract` | Web'den bilgi alma |
| **📱 Diğer** (1495) | — | Sınıflandırılamayan |

---

## 3. NASIL (How) — Yöntem

| Ana Başlık | Açıklama | Örnek |
|:-----------|:---------|:------|
| **🤖 Otomatik** (105) | Cron job, schedule, otomatik tetikleme | `cron`, `15-dk test`, `hermes cron tick` |
| **🎬 Video Öğrenme** (51) | YouTube → transcript → skill → hafıza | `yt-dlp + Whisper + OnceHafiza` |
| **🌐 Web Araması** (47) | Web'den araştırma, doğrulama | `web_search`, `web_extract` |
| **🧪 Test/Deneme** (41) | Pytest, deneme-yanılma | `pytest`, `simulasyon` |
| **🔧 Hata Çözümü** (33) | Hata tespit + düzeltme | `hata_cozumu`, `debug` |
| **👤 Kullanıcı Verdi** (27) | Kullanıcı tarafından direkt verilen bilgi | `manuel giriş` |
| **🧠 Hafıza Öncelikli** (25) | guven_skoru > 0.8 → direkt döndür | `OnceHafiza`, `hafiza-oncelikli-akis` |
| **📦 Diğer** (1444) | — | Sınıflandırılamayan |

---

## 4. NEDEN (Why) — Sebep

| Ana Başlık | Açıklama | Örnek Durumlar |
|:-----------|:---------|:---------------|
| **🤖 Otomasyon** (56) | Süreç otomasyonu, cron | Backup, test, rapor, güncelleme |
| **🔒 Güvenlik** (49) | Güvenlik önlemi, pentest | Port tarama, firewall, güvenlik denetimi |
| **✅ Test Doğrulama** (43) | Doğrulama, test | Pytest, benchmark, hata kontrolü |
| **🔧 Hata Düzeltme** (35) | Hata çözümü | Bug fix, hata_cozumu, debug |
| **📦 Kurulum** (24) | Yeni araç/uygulama kurulumu | npm, pip, setup, config |
| **📚 Öğrenme** (21) | Yeni bilgi öğrenme | Video izleme, web araştırma |
| **📊 Raporlama** (11) | Rapor oluşturma | Haftalık rapor, durum raporu |
| **📦 Diğer** (1534) | — | Sınıflandırılamayan |

---

## 5. KİM (Who) — Kaynak

| Ana Başlık | Açıklama | Sorumlu |
|:-----------|:---------|:--------|
| **🪟 Windows Ajanı** (84) | Windows terminal/otomasyon | `windows/windows-terminal-ajani` |
| **🧪 Test Ajanı** (59) | Test, benchmark, doğrulama | `reymen-test-runner (cron)` |
| **🎬 Video Ajanı** (47) | YouTube öğrenme | `video/video-ogrenme-ajani` |
| **⚙️ Hermes Core** (33) | Hermes sistemi | `hermes-agent`, `gateway` |
| **🤖 ReYMeN** (28) | ReYMeN kendi | `self-learning`, `once_hafiza` |
| **👤 Kullanıcı** (27) | Marko/Paşa | `kullanici`, `manuel` |
| **🐉 Kali Ajanı** (20) | Kali pentest | `kali/kali-nmap-servis-taramasi` |
| **📦 Diğer** (1475) | — | Otomatik/sınıflandırılamayan |

---

## Kategori Temizleme İstatistiği

| İşlem | Sayı |
|:------|:----:|
| 5N1K etiketi eklenen kayıt | 1773 |
| Temizlenen kategori adı | 455 |
| Kalan eski format kategori | ~300 |
| "Diğer" etiketli (NE) | 930 (%52) |

> **Sonraki adım:** "Diğer" etiketli kayıtların elle/manuel sınıflandırması gerek
