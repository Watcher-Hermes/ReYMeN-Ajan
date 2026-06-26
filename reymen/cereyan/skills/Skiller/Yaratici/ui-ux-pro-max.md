---
name: ui-ux-pro-max
title: "UI/UX Pro Max — Tasarım Zekası Asistanı"
description: "Use when designing UI/UX, generating design systems, finding color palettes, font pairings, UI styles, chart types, or UX best practices. BM25 search engine over 67 styles, 161 palettes, 57 fonts, 25 charts, 16 stacks."
tags: [ui, ux, design, style, color, typography, chart, design-system]
audience: contributor
category: software-development
license: MIT
author: NextLevelBuilder (adapted for ReYMeN Agent)
metadata:
  hermes:
    tags: [ui, ux, design, style, color, typography, chart, product, accessibility, design-system]
    related_skills: []
---
# UI/UX Pro Max — Tasarım Zekası Asistanı

UI/UX Pro Max, AI kod asistanları için tasarlanmış kapsamlı bir tasarım zekası skill paketidir. BM25 tabanlı arama motoru ile 67 UI stili, 161 renk paleti, 57 font çifti ve 161 endüstri akıl yürütme kuralı üzerinden tasarım sistemi önerileri üretir.

## Konum

```
.ReYMeN/scripts/ui-ux-pro-max/uipro.py  ← wrapper
.ReYMeN/scripts/ui-ux-pro-max/search.py ← ana arama motoru
.ReYMeN/scripts/ui-ux-pro-max/core.py   ← BM25 engine
.ReYMeN/scripts/ui-ux-pro-max/data/     ← CSV veritabanları
```

## Kullanım

### Domain Bazlı Arama

Tek bir domain'de arama yap:

| Domain         | Ne Bulur                              |
|----------------|----------------------------------------|
| `style`        | UI stilleri + CSS anahtar kelimeleri   |
| `color`        | Ürün tipine göre renk paletleri        |
| `chart`        | Grafik türü önerileri                  |
| `landing`      | Açılış sayfası desenleri + CTA         |
| `product`      | Ürün tipi → stil eşleme                |
| `ux`           | UX en iyi uygulamalar + anti-patterns  |
| `typography`   | Font çiftleri + Google Fonts import    |
| `icons`        | İkon kütüphanesi önerileri             |
| `react`        | React/Next.js performans               |
| `web`          | Web erişilebilirliği + HTML semantiği  |

**Örnekler:**
```bash
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "glassmorphism" --domain style
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "fintech banking" --domain product
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "healthcare" --domain color
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "elegant serif luxury" --domain typography
```

### Tasarım Sistemi Üretimi (Çoklu Domain)

5 domain'de paralel arama + 161 endüstri kuralı ile komple tasarım sistemi üretir:

```bash
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "SaaS dashboard" --design-system -p "MyApp"
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "beauty spa" --design-system -f markdown -p "Serenity Spa"
```

**Çıktı içeriği:** Pattern + Style + Colors (hex kodları) + Typography (Google Fonts URL) + Key Effects + Anti-patterns + Pre-delivery checklist.

### Stack Bazlı Arama

Desteklenen yığınlar: `react`, `nextjs`, `vue`, `svelte`, `angular`, `astro`, `flutter`, `swiftui`, `react-native`, `shadcn`, `html-tailwind`, `laravel`, `jetpack-compose`, `threejs`, `nuxtjs`, `nuxt-ui`

```bash
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "form validation" --stack react
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "responsive layout" --stack nextjs
```

### JSON Çıktı

Programatik kullanım için `--json` flag'i ekle:
```bash
python3 .ReYMeN/scripts/ui-ux-pro-max/uipro.py "glassmorphism" --domain style --json
```

## Veri Dosyaları

`~/.ReYMeN/scripts/ui-ux-pro-max/data/` altında CSV formatında:

| Dosya               | İçerik                              |
|--------------------|--------------------------------------|
| `styles.csv`       | 67 UI stili + CSS + AI prompt        |
| `colors.csv`       | 161 renk paleti + hex kodları        |
| `typography.csv`   | 57 font çifti + Google Fonts         |
| `charts.csv`       | 25 grafik türü + öneriler            |
| `landing.csv`      | Açılış sayfası desenleri             |
| `products.csv`     | 161 ürün tipi eşlemesi               |
| `ux-guidelines.csv`| 99 UX en iyi uygulama                |
| `ui-reasoning.csv` | 161 endüstri akıl yürütme kuralı     |
| `stacks/*.csv`     | 16 teknoloji yığını kılavuzu         |

## Ne Zaman Kullanılır

Kullanıcı şunları sorduğunda bu skill'i çağır:
- "X ürün tipi için hangi stili kullanmalıyım?"
- "X için komple tasarım sistemi tasarla"
- "Y endüstrisi için renk paleti bul"
- "Z ile hangi font iyi gider?"
- "Form validasyonu için UX en iyi uygulamalar"
- "X için açılış sayfası tasarla"
- "React erişilebilirlik kılavuzu"

## Mimari

**BM25 sıralama algoritması** (Elasticsearch ile aynı):
1. Sorgu ve dokümanları tokenize et
2. TF-IDF + uzunluk normalizasyonu ile sırala
3. Skoru > 0 olan ilk N sonucu döndür

**Tasarım sistemi üretimi:**
1. 5 domain'de paralel arama (product, style, color, landing, typography)
2. 161 endüstri kuralını uygula
3. Komple öneri olarak birleştir
