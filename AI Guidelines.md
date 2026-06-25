# AI Guidelines — ReYMeN Projesi

Bu dosya, ReYMeN projesine katkıda bulunan yapay zeka asistanlarının uyması gereken kuralları tanımlar.

## PROJE YAPISI

- **Kök:** `C:\Users\marko\Desktop\Reymen Proje\hermes_projesi`
- **Çekirdek:** `reymen/cereyan/` (beyin.py, motor.py, conversation_loop.py, once_hafiza.py, ajan_suru.py)
- **Araçlar:** `reymen/arac/web_search_tool.py`
- **Provider:** xiaomi/mimo-v2.5-pro (birincil), deepseek (fallback)
- **Botlar:** @Pasa_38_bot, @Kiral38bot, @ReYMeN_ReYMeNbot
- **Logging:** `reymen/sistem/reymen_logging.py` (get_logger() ile)
- **Hafıza:** `cereyan/.ReYMeN/ogrenmeler.db` (SQLite, OnceHafiza)

## ZORUNLU KURALLAR

### 1. Doğrulama
- Hiçbir şey uydurma. Dosyayı okumadan tahmin yürütme.
- Değiştirdiğin HER dosyayı ve satırı raporla.
- Test etmeden "oldu" deme. Her değişiklikten sonra `compile()` ile syntax kontrolü yap.

### 2. Hafıza-Öncelikli Çalışma
- Görev gelince ÖNCE `session_search` + `OnceHafiza.ara()` ile hafızaya bak.
- `guven_skoru > 0.8` ise direkt döndür (0 LLM çağrısı).
- Asla direkt uygulamaya atlama — önce mevcut pipeline'da aynı işi yapan adım var mı kontrol et.

### 3. Karar Döngüsü
Her önemli karardan sonra:
1. **Ne yaptın?** — somut, teknik
2. **Neden?** — gerekçe
3. **Alternatif düşündün mü?** — en az 1 alternatif

Cevapları `.ReYMeN/decisions.md`'ye kaydet.

### 4. Halüsinasyon Önleme
- Canlı veri sorgularında (fiyat, döviz, hava, haber) `auto_web_search.web_arasi_mi()` True ise `once_hafiza`'yı atla.
- Web sonucu varsa LLM'i tamamen atla (`web_arama_dogrulanmis`).
- `_tekrar_temizle()` ile 因为 loop, kelime tekrarı, 4000+ karakter kontrolü yap.
- API çağrılarında `frequency_penalty: 0.8` kullan.

### 5. Çift Lokasyon Kuralı
`once_hafiza.py` gibi iki kopyası olan dosyalarda (cereyan/ + sistem/) hata düzeltmesi HER İKİSİNE de uygulanmalı. Tek lokasyon yetmez.

### 6. Sessiz Onay
- Soru sor → 3 dk bekle.
- Cevap gelirse ona göre devam.
- 3 dk cevap yoksa → SESSİZ ONAY = onay say, devam et.
- Hiçbir bildirim/sayaç/bekleme yazısı gösterme.

### 7. No Goblins + Side Quest
- Gereksiz soru sorma, konudan sapma. Direkt ilerle.
- Yan görevleri `delegate_task` ile sub-agent'a yönlendir. Ana thread temiz kalsın.

### 8. Cave Modu
- Uzun süslü cevaplar yok. Direkt söyle.
- Format: Başlık(emoji+konu) → Kısa açıklama → Tablo (sütun başlıklı) → Alt not.

### 9. Güvenlik
- API key'ler asla koda yazılmaz. Sadece `.env` kullan.
- `write_file()` ile `.env`'ye yazma — terminal'de `echo >>` ile append yap.
- Kredi kartı/ödeme gerektiren işlemler yasak.

### 10. Dil
- Kullanıcı Türkçe konuşuyorsa Türkçe yanıt ver.
- Türkçe karakterleri (ğ, ü, ş, ı, ö, ç) doğru kullan.

### 11. Her Oturumun Başında — Hafıza Yükle
Önce `memory_bank.md` dosyasını oku ve projenin mevcut durumunu anla. Sonra kullanıcıya şunları söyle:
- Son ne yapıldı?
- Şu an hangi özellikler çalışıyor?
- Yarım kalan veya bilinen sorun var mı?
Anladıktan sonra "Hazırım, devam edebiliriz" de.
Kullanıcının onayını almadan hiçbir kod yazma.

### 12. Yeni Özellik Eklerken — Önce Plan
```
[ÖZELLİK]: ...buraya yaz...
```

Kodu yazmadan önce şunları listele:
1. Hangi dosyalara dokunacaksın?
2. Bu değişiklik hangi mevcut özellikleri etkileyebilir?
3. Risk taşıyan yerler neresi?

Kullanıcının onayını aldıktan sonra yaz. Bitince:
- Ne değiştirdiğini özetle
- Test etmen gereken eski özellikleri listele
- `memory_bank.md`'yi güncelle

### 13. Bug Düzeltirken — Önce Kök Sebep
```
[BUG]: ...buraya yaz...
```

Düzeltmeden önce:
1. Bu bug neden oluşuyor, kök sebebi nedir?
2. Düzeltmek için hangi dosyalara dokunacaksın?
3. Bu düzeltme başka neyi bozabilir?

Düzelttikten sonra:
- Testi geçirmek için test kodunu değiştirme
- Yaptığın değişikliği satır satır açıkla
- `memory_bank.md`'yi güncelle

## AKIŞ DİYAGRAMI

```
Görev gelir
  ↓
① session_search / OnceHafiza ara()
  ├─ guven > 0.8 → direkt döndür (LLM yok)
  └─ yok/belirsiz → devam
  ↓
② auto_web_search.web_arasi_mi()
  ├─ True → dogrulanmis_ara() → cache'e yaz → döndür
  └─ False → devam
  ↓
③ ONCELIK_CACHE (selam/teşekkür)
  ├─ eşleşme → direkt döndür
  └─ yok → devam
  ↓
④ LLM (beyin.uret_v2 / _cagir_openai_uyumlu_v2)
  ├─ frequency_penalty=0.8, max_tokens=4096
  └─ _tekrar_temizle() ile loop kontrolü
```
