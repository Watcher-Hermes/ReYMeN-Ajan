# ReYMeN Karar Kaydı (decisions.md)

## Karar #1 — Hangi Kural İlk Uygulanmalı?

**Tarih:** 21 Haziran 2026
**Bağlam:** 5 mühendislik kararı arasından ilk uygulanacak kural seçimi

### 1. Ne yaptın?
No Goblins kuralını ilk sıraya koydum. Diğer 4 kuralın (Concise Mode, Karar Döngüsü, Side Quest, Status Line) tamamı No Goblins olmadan işlevsiz kalıyor.

### 2. Neden?
Disiplin olmadan araç anlamsız. Önce gereksiz iş yapmayı bırak, sonra kalan araçları konuşlandır.

### 3. Alternatif düşündün mü?
- **Karar Döngüsü ilk:** Önce kayıt mekanizması kurulsun, sonra disiplin gelsin. Ama kayıt da olsa goblin yapmaya devam edersen kaydın anlamı kalmaz.
- **Concise Mode ilk:** Kısa konuş ama gereksiz iş yapmaya devam et. Tersi daha mantıklı.
- **Side Quest ilk:** Yan görevleri ayır ama ana thread'de goblin yapıyorsan fark etmez.

### Sonuç
Önce disiplin (No Goblins), sonra araçlar.

---

## Karar #2 — YouTube Video Talimatlarını Uygulama

**Tarih:** 21 Haziran 2026
**Bağlam:** "I Connected Claude to Power BI" videosu — 6 adımlı talimat seti

### 1. Ne yaptın?
Transcript alındı (328 satır), 6 talimat çıkarıldı. Power BI MCP server kurulumu + Power BI Desktop gerektiği için 1. adımda takıldı.

### 2. Neden?
Power BI Desktop sistemde yok. MCP server (`powerbi-modeling-mcp`) npm'de bulunamadı. Gerekli altyapı olmadan adımlar uygulanamaz.

### 3. Alternatif düşündün mü?
- **MCP server'ı manuel kur:** Kaynak kod varsa build et. Ama npm'de yayında değil — özel repo olabilir.
- **Alternatif MCP dene:** `powerbi-mcp` veya `@microsoft/powerbi-mcp` var mı kontrol et.
- **Power BI Web kullan:** Power BI Service üzerinden REST API ile bağlan. Ama video Desktop gösteriyor.

### Sonuç
Altyapı eksik → uygulanamadı. Power BI kurulumu + MCP server temini sonraki adım.

---

## Karar #3 — PowerBI "Yok" Hatasının Kök Neden Analizi

**Tarih:** 21 Haziran 2026
**Bağlam:** Kiral38 bot PowerBI Desktop'ı buldu, ben bulamadım. Aradaki fark ne?

### 1. Ne yaptın?
Hata analizi: 3 eksik adım tespit edildi:
1. **Yüzeysel arama** — Sadece `Program Files`'a baktım, Store App yolunu (`C:\Users\marko\Microsoft\`) atladım
2. **VS Code extension** — Hiç kontrol etmedim (Kiral38 buldu: Power BI Modelling MCP v0.4.0)
3. **Pes ettim** — "PowerBI yok" dedikten sonra alternatif aramadım. Kiral38 npm'den MCP server'ı kurdu, config'e ekledi, temizlik yaptı

### 2. Neden?
Sebep: "Yok" deme eşiğim çok düşük. 1-2 yöntemle arayıp bulamayınca hemen "yok" diyorum. Oysa 3 farklı yöntem + Store apps + hidden yollar taranmalı.

### 3. Alternatif düşündün mü?
- **find ile kapsamlı tarama:** `find /c/ -iname "*power*bi*"` yapsaydım Store App yolunu bulurdum
- **Get-StartApps:** PowerShell ile kayıtlı uygulamaları tarasaydım "Power BI Desktop" görünürdü
- **VS Code extensions klasörü:** `ls ~/.vscode/extensions/ | grep powerbi` ile extension bulunurdu

### Çözüm
Skill oluşturuldu: `reymen-kontrol-kurali` — "Yok" demeden önce 3 yöntemle kontrol et, altyapı eksikse pes etme.
Memory'e kural eklendi (limit dolu, kısmen eklendi).

---



---

## Karar #7 — Test Import Hataları Çözüldü

**Tarih:** 2026-06-21
**Bağlam:** `reymen/__init__.py` root shim'lerden import ediyordu → cirkuler import

### Ne yapıldı?
| # | Dosya | Değişiklik |
|---|-------|-----------|
| 1 | `reymen/__init__.py` | Root shim → doğrudan paket içi yol (`from reymen.cereyan.motor import Motor`) |
| 2 | `reymen/sistem/main.py` | Aynı düzeltme (13 import) |
| 3 | `reymen/cereyan/alt_ajan.py` | `from beyin` → `from reymen.cereyan.beyin` |
| 4 | `tests/test_vektorel_hafiza.py` | Shim import → `reymen.hafiza.vektorel_hafiza` |
| 5 | `vektorel_hafiza.py` (root shim) | `_BasitYedek`, `_budama_yap` private export eklendi |

### Neden?
Root shim'ler `from reymen.X.Y import *` yaparken, `reymen/__init__.py` de aynı modülleri root shim'den import ediyordu → Python modül başlatma çevrimi.

### Alternatif?
- sys.path sıra değişikliği (kırılgan)
- Tüm shim'leri kaldırmak (büyük değişiklik, riskli)
- Lazy import (semptom gizler)

### Test
`tests/test_vektorel_hafiza.py`: **27/27 PASSED** (önceden 0)


---

## Karar #8 — Self-Improvement: Hafıza Yönetimi (2. tur, İt. 9)

**Tarih:** 2026-06-21 18:19
**Bağlam:** Self-Improvement cron — Öncelikli görev (7 kategori import fix) zaten çözülmüştü (Karar #7). Normal rotasyona geçildi.

### 1. Ne yapıldı?
| # | İşlem | Detay |
|---|-------|-------|
| 1 | Öncelikli görev doğrulama | 30 test dosyası import OK, 1755 .py syntax OK, core modüller import OK. Kategorilerin tamamı çözülmüş |
| 2 | Geçiş protokolü | Mod B → Mod A: tüm kategoriler çözüldü, normal rotasyona dönüldü |
| 3 | MEMORY.md temizliği | 58 adet `[Hafıza]: İlgili tecrübe bulunamadı.` gürültü girişi kaldırıldı (13.1KB → 10.3KB) |
| 4 | Stale dosya temizliği | `.ReYMeN/gateway.pid` silindi |
| 5 | INDEX.md güncelleme | "2. tur ilerliyor — Hafıza ✅ → Planlama 🔜 (İt. 10)" |
| 6 | decisions.md güncelleme | Bu karar eklendi + Karar #4-6 eksik olduğu not edildi |

### 2. Neden?
- Öncelikli görev kategorileri önceki iterasyonlarda çözülmüş. Tekrar denemek anlamsız.
- MEMORY.md'deki gürültü (%45'i boş "ilgili tecrübe bulunamadı" girişleri) hafıza sorgulamalarında sinyal/gürültü oranını düşürüyor.
- `gateway.pid` eski (21 Haziran sabahından kalma), çalışan gateway yok.

### 3. Alternatif?
- **MEMORY.md'yi silmek**: Çok agresif, içinde kullanışlı OZET girişleri var
- **Eski session notlarını temizlemek**: 30+ dosya var ama cron geçmişi olarak değerliler — dokunulmadı
- **decisions.md'deki Karar #4-6'yı üretmek**: Orijinal kararların içeriği bilinmiyor, doldurmak yanıltıcı olur

### Durum
- Proje skoru: 99/100 (değişmedi)
- Öncelikli görev: ✅ Tamam (7/7 kategori çözüldü)
- Normal rotasyon: 2. turda Hafıza yönetimi ✅ → Sıradaki: Planlama (İt. 10)
- MEMORY.md: 13.1KB → 10.3KB (%21 küçüldü)
- Not: Root decisions.md'de Karar #4-6 eksik (doğrudan #3→#7 geçişi var)




---

## 🔍 Drift Tespiti Raporu — $(date +%Y-%m-%d\ %H:%M)

### Sonuç: 151 MODÜL DRİFT TESPİT EDİLDİ

Script: `scripts/duplicate_module_detector.py`
Exit Code: 1 (Drift mevcut)

### Kritik Bulgular

| Kategori | Adet | Açıklama |
|:---------|:-----|:---------|
| Kök ↔ Alt Modül Çakışması | ~40+ | `./mod.py` vs `./agent/mod.py` vs `./reymen/*/mod.py` |
| Eksik Fonksiyonlar | 150+ | Bir versiyonda olan fonksiyon, diğerinde yok |
| Test Dosyası Çoğaltımları | ~30+ | `tests/ReYMeN_reference/` alt çoğaltımları |

### Örnek Kritik Driftler

1. **auxiliary_client.py**: 100+ eksik fonksiyon (kök vs agent vs reymen)
2. **cli.py**: `agent/lsp/cli.py` ve `plugins/google_meet/cli.py` arasında massif fark
3. **bedrock_adapter.py**: 3 farklı versiyon, herbirinde eksik fonksiyonlar
4. **budget_config.py**: 3 farklı versiyon
5. **checkpoint_manager.py**: 3 farklı versiyon

### Öneri
- Eski kök-düzey stub dosyaları temizlenmeli
- Tek kaynak versiyon belirlenmeli (muhtemelen `reymen/` altındaki güncel versiyonlar)
- Kök-düzey dosyalar deprecated标记 konulmalı veya silinmeli

### Risk Seviyesi
**ORTA-YÜKSEK** — Import çakışmaları, beklenmeyen davranış, bakım yükü

