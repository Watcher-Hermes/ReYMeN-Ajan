---
name: duplicate-tespit
description: "Duplikasyon/Drift tespit sistemi. 2 script: full (264 satır, JSON/HTML/terminal çıktı) + basic (106 satır, terminal çıktı). Her cycle'da çalışır."
tags: [mimari, drift, duplicate, bakim]
---

# Duplicate / Drift Tespit

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | ReYMeN ajan (otonom döngü) |
| **Ne?** | Aynı isimli dosyaları AST ile karşılaştır, drift raporla |
| **Nerede?** | `scripts/duplicate_module_detector.py` (full), `scripts/duplicate_module_detector_basic.py` (basic) |
| **Ne Zaman?** | Her cycle başında + manuel |
| **Neden?** | Aynı isim + farklı klasör → "zaten var" sanılır, karşılaştırma yapılmaz. Kalıcı kural. |
| **Nasıl?** | AST → fonksiyon setleri → Jaccard benzerlik → canlı yol tespiti → rapor |

## Kullanım

```bash
# Full sürüm (detaylı çıktı)
python scripts/duplicate_module_detector.py . --format detayli

# JSON çıktı
python scripts/duplicate_module_detector.py . --format json

# Dosyaya kaydet
python scripts/duplicate_module_detector.py . --save .ReYMeN/raporlar/drift-$(date +%F).md

# Basic sürüm (hızlı tarama)
python scripts/duplicate_module_detector_basic.py .
```

## Kalıcı Kural

> Her cycle başında duplicate_module_detector.py otomatik çalışır.
> Aynı isimli dosya bulunursa, içerik karşılaştırması ZORUNLU.
> Hiçbir zaman iki kopya "geçici çözüm" olarak bırakılmaz.
> "Her şey temiz" raporu, bu kontrol çalıştırılmadan verilemez.

## İlişkili

- `scripts/duplicate_module_detector.py` (264 satır, full)
- `scripts/duplicate_module_detector_basic.py` (106 satır, basic)
- `.ReYMeN/raporlar/` — günlük tarama raporları
- `.ReYMeN/decisions.md` — kalıcı kural kaydı
