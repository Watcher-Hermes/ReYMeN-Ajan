---
name: duplicate-tespit
title: Çift/Kopya Modül Drift Tespiti
category: mimari
---

# duplicate-tespit

## 5N1K

| 5N1K | Açıklama |
|:-----|:---------|
| **Kim** | Hermes/ReYMeN projesindeki tüm geliştiriciler ve botlar |
| **Ne** | Çift lokasyonda bulunan aynı modüllerin drift (ayrışma) tespiti |
| **Nerede** | Proje kökünde `scripts/duplicate_module_detector.py` |
| **Ne Zaman** | Her cycle başında otomatik, manuel de çağrılabilir |
| **Neden** | once_hafiza.py gibi çift dosyalar zamanla farklılaşır (drift). Aynı fonksiyon iki yerde farklı çalışır → hata |
| **Nasıl** | AST analizi + hash karşılaştırması ile fonksiyon gövdeleri karşılaştırılır |

## Kullanım

```bash
# BASIC versiyon — AST fonksiyon karşılaştırması (kullanıcının istediği)
python scripts/duplicate_module_detector_basic.py . main.py

# FULL versiyon — Jaccard benzerlik + unused module tespiti (projede önceden vardı)
python scripts/duplicate_module_detector.py
python scripts/duplicate_module_detector.py --json
python scripts/duplicate_module_detector.py --path /path/to/proje
```

## Tespit Edilen Çiftler

| Dosya 1 | Dosya 2 | Açıklama |
|:--------|:--------|:---------|
| `cereyan/once_hafiza.py` | `sistem/once_hafiza.py` | OnceHafiza: modül-seviyesi vs sınıf |
| `cereyan/once_hafiza.py` | `once_hafiza.py` | Kök shim vs cereyan (beklenen fark) |

## Drift Skoru

- **0.0**: Birebir aynı
- **0.1-0.4**: Hafif drift (gözlem altında)
- **0.5-0.7**: Orta drift (manuel inceleme gerek)
- **0.8-1.0**: Ciddi drift (müdahale gerek)

Eşik: **0.1** üzeri drift uyarısı verir.

## Nasıl Çalışır

1. Her dosyayı `ast.parse()` ile ayrıştır
2. Fonksiyon/sınıf isimlerini ve gövdelerini çıkar
3. Gövde `hashlib.md5` hash'ini hesapla (dokstring hariç)
4. Ortak fonksiyon isimlerinde hash karşılaştırması
5. Sadece bir dosyada var olan fonksiyonları işaretle
6. Tüm farkları `drift_skoru` [0.0, 1.0] olarak özetle

## İlgili Dosyalar

- `scripts/duplicate_module_detector.py` — Full versiyon (önbellek + Jaccard)
- `scripts/duplicate_module_detector_basic.py` — Basic versiyon (AST fonksiyon karşılaştırma)
- `reymen/cereyan/once_hafiza.py` — Kaynak modül
- `reymen/sistem/once_hafiza.py` — Hedef/çift modül

## Oto-Çalıştırma (Cycle Integration)

Her cycle başında otomatik çalıştırmak için:

```python
# conversation_loop.py veya closed_learning_loop.py içinde
import subprocess
result = subprocess.run(
    ["python", "scripts/duplicate_module_detector.py", "--json"],
    cwd=PROJE_DIZINI, capture_output=True, text=True, timeout=120
)
findings = json.loads(result.stdout)
if findings:
    logger.warning(f"⚠️ {len(findings)} drift bulundu — cycle raporuna eklendi")
    # findings'i cycle raporuna ekle
```
