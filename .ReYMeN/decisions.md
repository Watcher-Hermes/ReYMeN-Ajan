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
