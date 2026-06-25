# Proje Amaçları — ReYMeN

## Vizyon
Türkçe konuşan, çoklu sağlayıcı destekli, otonom AI ajan. Hermes Agent fork'u.

## Fiziksel Yapı

| Öğe | Değer |
|:----|:------|
| **Kök dizin** | `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi` |
| **Çekirdek modüller** | `reymen/cereyan/` (beyin, motor, conversation_loop, once_hafiza, ajan_suru) |
| **Araçlar** | `reymen/arac/` (web_search_tool) + `reymen/tools/` |
| **Hafıza DB** | `cereyan/.ReYMeN/ogrenmeler.db` (SQLite, OnceHafiza) |
| **Logging** | `reymen/sistem/reymen_logging.py` (get_logger) |
| **Kararlar** | `.ReYMeN/decisions.md` |
| **Bot profilleri** | default (@Pasa_38_bot), reymen (@ReYMeN_ReYMeNbot), kiral38 (@Kiral38bot) |

## Provider Zinciri

```
xiaomi/mimo-v2.5-pro (birincil)
  → deepseek/deepseek-chat (kredi bitince)
  → xai/grok-2-latest
  → groq/llama-3.3-70b-versatile
  → openrouter
  → lmstudio (son çare)
```

## Temel Hedefler

| # | Hedef | Metrik |
|:-:|:------|:-------|
| 1 | **Tutarlılık** | Aynı sorgu → aynı kalite cevap |
| 2 | **Verimlilik** | Cache/hafıza ile LLM çağrılarını %60 azalt |
| 3 | **Güvenilirlik** | Halüsinasyon = 0, döngü = 0 |
| 4 | **Genişletilebilirlik** | Yeni provider/araç < 10 dk ekleme |

## Kapsam (Ne YAPILIR / Ne YAPILMAZ)

| Yapılır | Yapılmaz |
|:--------|:---------|
| web_search ile canlı veri çekme | LLM'den fiyat/döviz uydurma |
| OnceHafiza'ya kaydetme/öğrenme | Bilinmeyen kaynaktan kod çalıştırma |
| Hata bul → düzelt → test et | "Denedim olmadı" bırakma |
| Türkçe yanıt | Kredi kartı/ödeme işlemi |
| MCP entegrasyonu | overengineering / gereksiz şişirme |

## Bilinen Hatalar / Riskler

| Risk | Şiddet | Durum |
|:-----|:-------|:------|
| Çince loop (因为) — LLM sonsuz üretim | KRİTİK | ✅ _tekrar_temizle() + frequency_penalty fix |
| Cache miss → drift döngüsü | YÜKSEK | ✅ Canlı veri bypass + döngü kırıcı fix |
| JSON truncation (icerik[:200]) | ORTA | ✅ 200→2000 fix |
| API key'leri .env'de | DÜŞÜK | ✅ write_file yasak, echo ile append |
| Provider kredisi bitince fallback | ORTA | ✅ Multi-provider zincir |

## Sapma Önleme (AI Asistanı İçin)

### Karar Ağacı
```
Talep gelir
  ↓
Kapsamda mı? (ReYMeN ile ilgili mi?)
  ├─ EVET → Memory Bank'i oku, OnceHafiza'ya bak, uygula, kaydet
  └─ HAYIR → "Bu proje kapsamında değil" de, reddet
  ↓
3 soru: Ne yaptın? Neden? Alternatif?
  ↓
decisions.md + Memory Bank güncelle
```

### Sapma Alarmları
- ❗ Başka bir projenin koduna dalıyorsan = SAPMA
- ❗ Sorulanla ilgisiz bir şey yapıyorsan = SAPMA
- ❗ Dosyayı okumadan değiştiriyorsan = SAPMA
- ❗ "şunu da eklesek iyi olur" ile şişiriyorsan = SAPMA
