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
