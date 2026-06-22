# 🏆 Kazanımlar ve Öğretimler

## Geçmiş Kayıtlar (21 Haziran 2026)

---

## ⚙️ ReYMeN Mühendislik Kararları

### Karar #1 — Hangi Kural İlk Uygulanmalı?
**Kazanım:** Önce disiplin (No Goblins), sonra araçlar. Diğer 4 kural (Concise Mode, Karar Döngüsü, Side Quest, Status Line) No Goblins olmadan işlevsiz.

### Karar #2 — YouTube Video Talimatlarını Uygulama
**Kazanım:** Altyapı eksik → uygulanamadı. Power BI Desktop sistemde yok, MCP server npm'de bulunamadı. Önce altyapı kontrolü.

### Karar #3 — PowerBI "Yok" Hatasının Kök Neden Analizi
**Kazanım:** "Yok" deme eşiği çok düşüktü. 1-2 yöntemle arayıp bulamayınca hemen "yok" denmemeli. 3 farklı yöntem + Store apps + hidden yollar taranmalı.
**Çözüm:** Skill oluşturuldu: `reymen-kontrol-kurali`

### Karar #7 — Test Import Hataları Çözüldü
| # | Dosya | Değişiklik |
|---|---|---|
| 1 | `reymen/__init__.py` | Root shim → doğrudan paket içi yol |
| 2 | `reymen/sistem/main.py` | Aynı düzeltme (13 import) |
| 3 | `reymen/cereyan/alt_ajan.py` | `from beyin` → `from reymen.cereyan.beyin` |
| 4 | `tests/test_vektorel_hafiza.py` | Shim import → `reymen.hafiza.vektorel_hafiza` |
| 5 | `vektorel_hafiza.py` (root shim) | Private export eklendi |
**Test:** `tests/test_vektorel_hafiza.py`: **27/27 PASSED** (önceden 0)

### Karar #8 — Self-Improvement: Hafıza Yönetimi (2. tur, İt. 9)
| # | İşlem | Detay |
|---|---|---|
| 1 | Öncelikli görev doğrulama | 30 test dosyası import OK, 1755 .py syntax OK |
| 2 | Geçiş protokolü | Mod B → Mod A: tüm kategoriler çözüldü |
| 3 | MEMORY.md temizliği | 58 gürültü girişi kaldırıldı (13.1KB → 10.3KB) |
| 4 | Stale dosya temizliği | `.ReYMeN/gateway.pid` silindi |

---

## 🧠 OnceHafiza Sistemi

| # | Değişiklik | Açıklama |
|---|---|---|
| 1 | Kademeli güven (sigmoid) | `guven = 1 / (1 + e^(-0.5 * (basari - hata - 1)))` |
| 2 | İlk kayıt guven=0.5 | Eski: 1.0 → Yeni: 0.5 (daha gerçekçi) |
| 3 | `kaynak_url TEXT` kolonu | Her kayıt için kaynak URL ayrı tutulur |
| 4 | Web tetikleyici sistemi | 5 tetikleyici (boş, düşük güven, hata, geçerlilik, çelişki) |
| 5 | `kategori` kolonu | "kali", "dron", "cad" — farklı ajan kendi kategorisine baksın |
| 6 | `gecerlilik_tarihi` kolonu | Bugün + 6 ay — eski bilgi tespiti |

**DB Konumu:** `reymen/cereyan/.ReYMeN/ogrenmeler.db` (55 kayıt)
**Güven Hesaplama:** `guven = basari / (basari + hata)`
**Okuma API:** `OnceHafiza.hafizada_ara(hedef)` → `son_kullanim` + `guven_skoru` otomatik güncelle
**Kaydetme API:** `kaydet(hedef, cozum, kategori="kali|dron|cad", kaynak_url="...")`

---

## 🕸 Web Tetikleyici Sistemi

5 tetikleyici ile ajanın ne zaman web'e gideceğini belirleme:

| # | Tetikleyici | Koşul | Puan |
|:-:|:------------|:------|:----|
| 1 | T1: Hafıza boş | COUNT=0 | 1.0 |
| 2 | T3: Görev başarısız | hata >= 2 | 0.8 |
| 3 | T2: Güven düşük | guven < 0.5 | 0.5-0.3 |
| 4 | T4: Geçerlilik aşmış | tarih < bugün | 0.3 |
| 5 | T5: Çelişki | iki kaynak farklı | 0.6-0.4 |

---

## 🎬 Video Öğrenme Ajanı

YouTube/Video'dan skill çıkarma pipeline'ı:
1. yt-dlp ile video bilgisi + altyazı
2. Metni bölümlere ayır
3. Kod/komut/kavram → skill
4. Hafızadaki eski bilgiyle karşılaştır
5. Hata tespit et (try/except eksik, timeout yok, sonuç parse edilmemiş)
6. Birleşik skill kaydet: `video/<dil>/<konu>`

---

## 🔍 Belirsiz Görev Çözümü

Belirsiz görev geldiğinde önce hafızayı kontrol et:

| Kategori | Tetikleyici Kelimeler |
|:---------|:----------------------|
| kali/network/nmap | güvenli, port, tarama, nmap, ağ, servis, pentest |
| kali/web | web, site, sql, xss, burp |
| cross-platform/security | koordinasyon, inter-agent, güvenlik, engelle |
| windows/terminal/network | windows, ipconfig, netstat, firewall |
| windows/terminal/system | systeminfo, tasklist, servis |
| dron | dron, drone, uçur, px4, uav |
| cad | cad, solidworks, çizim, 3d |
| video/python/nmap | video, python, nmap, öğren |

**Öneri formatı:** "X dedin. Hafızamda en çok Y ile ilgili kayıtlarım var. Z'den başlayalım mı?"
**Puan formülü:** `kelime_eslesme(x0.3) + hafiza_guven(x0.7)`

---

## 🛠 Skill'ler (Hermes)

| Skill | Kategori | Açıklama |
|:------|:---------|:---------|
| `belirsiz-gorev-cozumu` | — | Belirsiz görevlerde hafızadan kategori bul + öner (✅ GitHub) |
| `web-tetikleyici-sistemi` | — | 5 tetikleyici ile web'e gitme kararı (✅ GitHub) |
| `video-ogrenme-ajani` | — | Video → transcript → skill → hafıza (✅ GitHub) |
| `self-improvement-loop` | devops | 15dk'da bir 5 alan rotasyonu (Hafıza/Plan/Kod/Hız/Hata) |
| `hermes-agent-skill-authoring` | devops | SKILL.md yazma rehberi |
| `reymen-kontrol-kurali` | — | "Yok" demeden önce 3 yöntemle kontrol et (✅ Yerel) |
| `windows-terminal-ajan` | — | Windows terminal çıktılarını analiz et (✅ Yerel) |
| `systematic-debugging` | devops | 4 aşamalı hata ayıklama |
| `test-driven-development` | devops | TDD: RED-GREEN-REFACTOR |
| `requesting-code-review` | devops | Pre-commit güvenlik taraması |
| `github-code-review` | github | PR review, inline comments |
| `github-pr-workflow` | github | PR lifecycle |
| `github-issues` | github | Issue yönetimi |
| `plan` | devops | Plan yazma |
| `simplify-code` | devops | 3-ajanlı kod temizliği |
| `node-inspect-debugger` | devops | Node.js Chrome DevTools debug |
| `kanban-orchestrator` | devops | Görev bölme + anti-temptation |
| `kanban-worker` | devops | Kanban worker pitfall'ları |
| `dogfood` | devops | Web app QA |
| `exc` + `p5js` + `claude-design` + `sketch` + `popular-web-designs` | creative | HTML/JS/sketch araçları |
| `ascii-art` + `ascii-video` + `architecture-diagram` | creative | ASCII/terminal görsel |
| `llama-cpp` | mlops | Local GGUF inference |
| `weights-and-biases` | mlops | ML experiment tracking |
| `jupyter-live-kernel` | data-science | Live Jupyter kernel |
| `arxiv` + `llm-wiki` + `blogwatcher` + `polymarket` | research | Araştırma/izleme |
| `youtube-content` | media | YouTube transcript → özet |
| `songwriting-and-ai-music` + `heartmula` | creative | Müzik/söz yazma |
| `obsidian` | note-taking | Obsidian not defteri |
| `google-workspace` | productivity | Gmail, Calendar, Drive |
| `notion` | productivity | Notion API |
| `airtable` | productivity | Airtable REST API |
| `nano-pdf` | productivity | PDF düzenleme |
| `maps` | productivity | Harita/geocode |
| `github-auth` + `github-repo-management` | github | GitHub auth/repo yönetimi |
| `huggingface-hub` | mlops | HuggingFace model yönetimi |
| `audiocraft` + `segment-anything-model` + `stable-diffusion` | mlops | Model araçları |
| `claude-code` + `opencode` + `codex` | autonomous-ai-agents | Autonomous coding agents |
| `agent-fork-maintenance` | devops | Fork senkronizasyonu |
| `upstream-fork-comparison` | devops | Upstream karşılaştırma |
| `error-handling-audit` | devops | Hata yönetimi denetimi |
| `python-codebase-reorganization` | devops | Python kod yapısı düzenleme |
| `python-error-handling-audit` | devops | Python hata yönetimi denetimi |
| `humanizer` | creative | AI metni insanlaştırma |
| `comfyui` | creative | ComfyUI ile görsel/video/audio |
| `manim-video` | creative | 3Blue1Brown tarzı animasyon |
| `touchdesigner-mcp` | creative | TouchDesigner kontrol |
| `a2a-agent-spec` | — | A2A Agent Card + skills şeması |
| `a2a-integrator` | — | A2A entegrasyon tasarımı |
| `hermes-agent` | — | Hermes Agent yapılandırma/rehber |
| `claude-design` | creative | Tek seferlik HTML artifact |
| `design-md` | creative | Google DESIGN.md token spec |
| `pretext` | creative | Browser demo oluşturma |
| `songsee` | media | Audio spectrogram |
| `teams-meeting-pipeline` | productivity | Teams toplantı pipeline |
| `ocr-and-documents` | productivity | PDF/scan metin çıkarma |
| `powerpoint` | productivity | .pptx düzenleme |
| `yuanbao` | yuanbao | Yuanbao grup yönetimi |
| `openhue` | smart-home | Philips Hue kontrol |
| `himalaya` | email | IMAP/SMTP email |
| `gif-search` | media | Tenor GIF arama |
| `baoyu-infographic` | creative | 21 layout × 21 stil infografik |
| `spike` | devops | Throwaway deney |
| `upstream-release-check` | — | Upstream release kontrolü |
| `planlama-scan` | — | Planlama tarama |

---

## 🐛 Sistem Hata Analizi (13 Hata — 5 Kategori)

| Kategori | Hata | Durum |
|:---------|:-----|:------|
| K1 — Web tetikleyici | T4 içerik güncelliği kontrolü yok | ⏳ Çözüm bekleme |
| K1 — Web tetikleyici | T2 hiç ateşlenmez (guven<0.5 kayıt yok) | ❌ Devam ediyor |
| K2 — Puanlama | Kod yok, sadece AGENTS.md'de | ❌ Kodlanacak |
| K3 — DB | %90.7 kayıt guven=1.0 (şişirilmiş) | ✅ Düzeltildi (H16) |
| K4 — Cross-agent | Kod yok, timeout yok, mesaj kaybı garantisi | ❌ Kodlanacak |
| K5 — Zehirli hafıza | 1 başarıda guven=1.0 çok yüksek | ✅ Sigmoid ile düzeltildi |

---

## 📝 Kullanıcı Hafızası (USER.md — Hermes)

**Kullanıcı:** Q! (Telegram)
**Host:** Windows 10
**Proje:** ReYMeN Agent — Hermes fork'u
**İletişim:** Türkçe (Cave Modu), Telegram öncelikli
**Kurallar:** No Goblins, Karar Döngüsü, Cave Modu, Side Quest, Status Line
**Tercihler:**
- Kısa rapor + tablo formatı
- 15dk cron raporları Run #N formatında
- kazanimlar.md tüm kazanım/skill/memory'yi tutar
- decisions.md her karar kaydı

---

## 🔄 Self-Improvement Loop

**Schedule:** `*/15 * * * *` (15dk'da bir)
**Repeat:** 30 iterasyon
**Durum:** 14/30 tamam — cron fix'lendi (pytest --collect-out hang'i kaldırıldı)
**Alan rotasyonu:** Hafıza → Planlama → Kod → Hız → Hata
**Kalan:** 16 iterasyon

---

## 🚨 Ciddi Pitfall'lar (Kesinlikle Unutma)

| # | Pitfall | Çözüm |
|:-:|:--------|:------|
| 1 | `pytest --collect-only` HANG yiyor | `compile()` + `timeout 5 import` kullan |
| 2 | Memory'de gürültü birikimi | Her hafıza turunda `İlgili tecrübe bulunamadı`'yı temizle |
| 3 | Cron tick'leri terminal bloke olunca atlamaz | Background terminal kullanma, foreground + timeout yeter |
| 4 | decisions.md'de karar yazıldı sanıp okumamak | Her karar yazdıktan sonra `read_file` ile teyit et |
|| 5 | Mod B'de kategoriler önceden çözülmüş olabilir | Her iterasyon başında kategori doğrulaması yap |

---

## 21 Haziran 2026 — 21:45 — Hafıza Yönetimi (3. tur İt. 14)

**Kazanım:** Karar #16 gap tespit edildi ve düzeltildi — önceki cron (İt. 13, Hata düzeltme) decisions.md'ye yazamamış. "0 hata" dahi kaydedilmeli. 3. tur Hafıza yönetimi ✅: stale state dosyası bulunamadı (proje temiz), INDEX.md ↔ decisions.md tutarlılık sağlandı, Karar #17 eklendi.

---
## 21 Haziran 2026 — 21:50 — Hermes Agent (Ben)

**Kazanım:** Tüm memory/skill/kayıtlar TEK dosyada: .ReYMeN/kazanimlar.md. Hermes memory tool (`memory`) kullanılmayacak — çünkü Hermes internal (`AppData/.../kiral38/memories/`) diğer ajanların erişemediği yer. Tüm ajanlar ortak dosyaya append eder.

---
## 21 Haziran 2026 — Self-Improvement cron — Planlama (3. tur İt. 15)

**Kazanım:** Proje compile + import taraması: 3321 .py syntax OK, 9/9 core modül import OK, 145 test syntax OK. Kırık import yok — sistem sağlam. Karar #18 decisions.md'ye eklendi. INDEX.md güncellendi.

---
## 21 Haziran 2026 22:15 — Hermes — Kod Kalitesi
.ReYMeN/scripts/code_quality_scan.py scripti olusturuldu (AST tabanli 5 kontrol: bare-except, BOM, syntax, TODO, large files). 6 bare-except (skill script'leri), 0 BOM, 3191/3191 syntax OK, 7 code marker, 443 large files.

---
## 21 Haziran 2026 22:45 — Hermes — Hız (Alan 4)
Pyclean: 108.6MB freed (252 dirs). Big files: 457 >500 satır. session.db: 464KB normal. INDEX.md güncellendi. Karar #21 (öncesinde duplicate #19→#20 fix).

---
## 21 Haziran 2026 — Hermes — Hata düzeltme (Alan 5) — İt. 18
Bandit taraması (21 HIGH, 69 MEDIUM, 614 LOW), syntax 259 dosya 0 hata, 18 test passed. Import fix (AIAgent path). Karar #22. _(INDEX.md güncellemesi atlanmıştı — İt. 19'da düzeltildi)_

---
## 21 Haziran 2026 — Hermes — Hafıza (Alan 1) — 4. tur İt. 19
Parial Write gap fix: İt. 18 decisions.md vardı INDEX.md yoktu → düzeltildi. INDEX.md onarım (birleşik satır). Stale file check temiz. MEMORY.md 10 satır/1803 char — gürültü yok. Duplicate check temiz. Karar #23. 4. tur başladı.

---
## 2026-06-21 17:30 — Hermes — Planlama (Alan 2)
Karar #24 — Cron Iteration 20: Planlama taraması yapıldı. 3197 py dosyası syntax ✅, 12/12 core modül import ✅, 1759 test dosyası syntax ✅. Sistem stabil.

---
## 2026-06-21 23:20 — ReYMeN — Hız (Alan 4)
Pycache temizliği: 77.3MB freed (250 dirs). Big files: 444 (>500 lines). session.db: 464KB (normal). INDEX.md gap (Yön B) fixed: Karar #25'ten sonra INDEX.md güncellenmemişti, düzeltildi. Karar #26 eklendi.
