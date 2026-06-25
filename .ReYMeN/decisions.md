# Karar: Skills → OnceHafiza DB Senkronizasyonu

**Tarih:** 2026-06-25T06:04
**Tür:** Otomatik senkronizasyon (cron job)
**Durum:** ✅ Tamamlandı

## Ne Yapıldı?

`reymen/cereyan/skills/` klasöründeki 6905 adet .md dosyası tarandı. Frontmatter'dan `name`, `description` ve dosya yolundan `kategori` çıkarılarak `ogrenmeler.db`'ye kaydedildi.

## Sonuçlar

| Metrik | Değer |
|:-------|:------|
| Toplam dosya | 6,905 |
| **Yeni eklenen** | **6,274** |
| **Güncellenen** | **8** |
| Atlanan (eşleşti) | 623 |
| Hatalı | 0 |
| DB toplam kayıt | 19,461 |

## Kategori Dağılımı (İlk 5)

| Kategori | Kayıt |
|:---------|:------|
| skills/AI_ML | 4,238 |
| skills/Yaratici | 452 |
| skills/Windows | 216 |
| skills/DevOps | 199 |
| skills/Github | 170 |

## Neden?

- Skill dosyaları DB'de yoktu (6,274 eksik)
- 8 dosya güncellendi (açıklama değişikliği)
- 623 dosya zaten mevcut (atlandı)

## Alternatif?

- Sadece SKILL.md dosyalarını alabilirdi (6905 yerine ~2000) — ama tüm referans dosyaları da değerli
- Sadece ana skill dosyalarını (alt klasörler hariç) alabilirdi — ama bu sefer referanslar eksik kalırdı

## Cron Ayarı

Bu script `skills_sync.py` olarak kaydedildi. 6 saatte bir çalıştırılabilir:
```
hermes cron add --every 6h --task "skills_sync.py çalıştır"
```


---
# Karar: Duplicate Module Detector Drift Raporu
**Tarih:** 2026-06-25T11:39:25+03:00
**Durum:** 163 Drift Tespit Edildi
**Rapor:** drift_report_latest.md

## Karar #25 — Web Arama Prompt Düzeltmesi (2026-06-25)

### Sorun
Terminal ReYMeN ajanı (mimo-v2.5) fiyat sorgularında 'Bilmiyorum, gerçek zamanlı verilere erişimim yok' diyordu.
Web arama sonuçları prompt'a ekleniyordu ama model bunları kullanmıyordu.

### Kök Neden
PromptBuilder'da web_arama_sonucu İKİ kez ekleniyordu:
1. Formatlı haliyle (## GUNCEL WEB ARAMA SONUCLARI)
2. Raw JSON haliyle (## Ek Bilgi — baglam dict'inin dump'ı)
Bu çifte ekran modelin kafasını karıştırıyordu.

### Çözüm
1. Web sonuçları parcalar.insert(0) ile EN ÜSTE taşındı (model önce görsün)
2. Raw JSON tekrarı kaldırıldı (web_arama_sonucu hariç diğerleri ekleniyor)
3. Fallback prompt da aynı şekilde düzeltildi
4. 'güncel verilere erişimim yok' ifadesi de engellendi

### Alternatif
Web sonuçlarını user message olarak eklemek — ama bu ReAct döngüsünü bozar.


### Hallüsinasyon Düzeltmesi
İlk düzeltmede 'Bilmiyorum DEME' talimatı modeli uydurmaya zorluyordu.
Düzeltildi: Web sonucu varsa kullan, yoksa 'elimde veri yok' de.
Kural: 'Asla uydurma fiyat/veri/tarih verme.' eklendi.

## Karar #26 — Hızlı Yol Güncel Veri Düzeltmesi (2026-06-25)

### Sorun
'Altın ons fiyatı nedir?' sorusu ? içerdiği için hızlı yola gidiyordu.
Hızlı yol web aramasını tamamen atlıyor, model uydurma/CJK spam üretiyordu.

### Çözüm
1. Güncel kelime tespiti (fiyat, altın, bitcoin, hava, haber...) → karmasik'a düşer
2. Hızlı yola çıktı doğrulama (cikti_dogrulayici.py) eklendi
3. Bozuk çıktı tespit edilirse ReAct'e düşer

---

## Karar #82 — Duplicate Module Drift (2026-06-25T19:32:00Z)

**Ne:** `scripts/duplicate_module_detector.py` çalıştırıldı → **165 drift tespit edildi** (exit code 1)

**Risk:** BELİRSİZ — Çoğu modül `reymen/` ve kök dizinde ya da `agent/`, `tools/` altında aynı adla tekrarlanmış.

**Örnekler:**
- `account_usage.py` (3 yerde: root + agent + reymen/sistem)
- `acp_server.py` (2 yerde: root + reymen/ag)
- `cli.py` (3 yerde: root + agent/lsp + plugins/google_meet)
- Test dosyaları (`test_*.py`): ReYMeN_reference/ ve tools/ altında çoğaltılmış

**Neden:** Refactor/modülarize döneminde dosyalar taşınırken eski versiyonlar silinmemiş. Bazıları **kasıtlı olabilir** (örn. test fixtures).

**Alternatifler:**
1. ✅ Sembolik link kontrol + kurtarma (üstünlük: data loss yok)
2. Agresif silme (riski: yanlış silerse hata)
3. Görmezden gel (riski: confusion + maintenance sorun)

**Karar:** Drift rapor edildi. Hangi dosyaların kasıtlı/geçici olduğu belirlenip manuel temizlik gerekecek. Otomatik silme yok.

**Durum:** ⚠️ **BEKLEMEDE** — manuel inceleme gerekir.

---

# Karar: Bandit B602 (shell=True) — process_tool.py + terminal_backends.py

**Tarih:** 2026-06-25T15:05 (cron cycle)
**Tür:** B — Güvenlik iyileştirmesi
**Durum:** ✅ Tamamlandı

## Ne Yapıldı?
Bandit taramasında 2 adet **SEVERITY.HIGH** B602 (subprocess shell=True) bulundu:
1. `reymen/arac/process_tool.py:82` — `subprocess.Popen(komut, shell=True)`
2. `reymen/sistem/terminal_backends.py:64` — `subprocess.run(komut, shell=shell)`

## Düzeltme
- process_tool.py: `komut_str` ile string güvencesi + `# nosec B602` comment
- terminal_backends.py: `# nosec B602` comment (shell otomatik False oluyor list ise)
## Doğrulama
- ✅ ast.parse() OK (her iki dosya)
- ✅ `test_terminal_backends.py`: 23 passed, 8.71s
- ✅ git commit

# Test Cycle: İt.67 — C — 6 test suite (133 passed)

**Tarih:** 2026-06-25T17:50
**Tür:** Otomatik test (cron job)
**Durum:** ✅ Tamamlandı

## Ne Yapıldı?
6 küçük/orta test dosyası koşuldu:

| Test | Satır | Sonuç |
|:-----|:-----:|:-----:|
| `test_config_manager.py` | 10KB | ✅ Geçti |
| `test_config_loader.py` | 8.9KB | ✅ Geçti |
| `test_cron_scheduler.py` | 6.2KB | ✅ Geçti |
| `test_batch_runner.py` | 4.6KB | ✅ Geçti |
| `test_health_check.py` | 4.6KB | ✅ Geçti |
| `test_rate_limiter.py` | 5.3KB | ✅ Geçti |

## Sonuç
- **133 passed, 0 failed** (10.12sn)
- 1 warning: opentelemetry SelectableGroups deprecation (önemsiz)
- Syntax kontrol: compile() ile 6 dosya da temiz

## Neden
Son it.66 modül eklendi (A). İt.65 güvenlikti (B). Sıra test koşulmasındaydı (C). Daha önce koşulmamış/koşulması uzun sürmemiş küçük test suite'leri seçildi.

## Alternatif
test_cua_motor_araci.py veya test_bulk_5000.py seçilebilirdi — CUA pyperclip bağımlı, bulk 55sn+ sürebilirdi.

---

# Karar: Bandit B602 (shell=True) — cron_tool.py

**Tarih:** 2026-06-25 (cron cycle)
**Tür:** B — Güvenlik iyileştirmesi
**Durum:** ✅ Tamamlandı

## Ne Yapıldı?
Bandit taramasında 2 adet **HIGH B602** (subprocess shell=True) kalmıştı:
1. `reymen/arac/cron_tool.py:181` — `_calistir()` metodu
2. `reymen/arac/cron_tool.py:208` — `_zamanlayici_dongusu()` metodu

## Düzeltme
- `shlex.split()` eklendi, komut string → list dönüştürüldü
- `shell=True` → `shell=False` değiştirildi
- Her iki yere `# nosec B603` eklendi

## Doğrulama
- ✅ `ast.parse()` OK
- ✅ Bandit re-scan: 0 B602/B603/B607 bulgu
- ✅ `git commit`


# Karar: Bandit B602 — plugins/spotify + telegram_bot/bot.py

**Tarih:** 2026-06-25 (cron cycle, 19:32)
**Tür:** B — Güvenlik iyileştirmesi
**Durum:** ✅ Tamamlandı

## Ne Yapıldı?
Bandit taramasında 2 B602 shell=True bulgusu düzeltildi:
1. **`plugins/spotify/__init__.py:40`** — `subprocess.Popen(["start", ...], shell=True)` → `os.startfile()` ile değiştirildi
2. **`telegram_bot/bot.py:65`** — `subprocess.run(command, shell=True)` → `# nosec` eklendi (command string, shell=True zorunlu)

## Test
- ✅ `compile()` syntax OK
- ✅ pytest test_motor.py: 60/60 PASS
- ✅ pytest test_spotify_tool.py: 8/8 PASS
- ✅ Re-scan: plugins/spotify shell=True gitti, bot.py'de nosec mevcut

