# ReYMeN Self-Improvement Döngüsü

Kullanıcı tarafından sağlanan 6 adımlı aktif kendini geliştirme metodolojisi. 
Hata düzeltme, test ekleme ve yetenek geliştirme için uygulanır.

---

## Döngü Akışı

```
ADIM 1 — GÖZLEM (pytest + log)
ADIM 2 — TEŞHİS ([KOD]/[BİLGİ]/[TOOL] kategorisi)
ADIM 3 — ARAŞTIR (hafıza→GitHub→arXiv→web→Claude)
ADIM 4 — KARAR VER (UYGULA/REDDET/DAHA_FAZLA)
ADIM 5 — TEST ET (sandbox → pytest doğrula)
ADIM 6 — UYGULA VE KAYDET (dosya + skill + decisions.md)
```

---

## ADIM 1 — GÖZLEM

```bash
# Testleri çalıştır
pytest tests/ReYMeN_reference/acp/ -v --tb=long
# Hata loglarını oku
cat log/*.log
```

**Ne sor:** Hangi testler başarısız? Neden? Hangi görevlerde yavaşladım? 
Hangi hatayı daha önce de yaptım? Eksik fonksiyon/değişken/modül var mı?

---

## ADIM 2 — TEŞHİŞ (3 Kategori)

| Kod | Anlamı | Örnek |
|:----|:-------|:------|
| **[KOD]** | Dosyada eksik/yanlış | `test_auth.py başarısız ÇÜNKÜ auth.py'de TERMINAL_SETUP_AUTH_METHOD_ID yok` |
| **[BİLGİ]** | Nasıl yapılacağını bilmiyorum | Flask middleware pattern bilinmiyor |
| **[TOOL]** | Gerekli araç bağlı değil | Power BI Desktop kapalı, rg/find kurulu değil |

Her hata için kök neden yaz: `"neden X başarısız ÇÜNKÜ ..."`

---

## ADIM 3 — ARAŞTIR (Sıralı)

Şu kaynakları sırayla tara, birinde bulunca dur:

| Sıra | Kaynak | Ne Aranır | 
|:----:|:-------|:----------|
| 1 | Kendi hafıza | `session_search(query="...")` |
| 2 | GitHub | `web_search("[arac python implementation] github")` |
| 3 | arXiv/docs | `web_search("[konu] best practice python")` |
| 4 | Web | `web_search("[hata mesajı] nasıl çözülür")` |
| 5 | Dış LLM (Claude vb.) | Alt ajan ile danış |
| 6 | Manuel araştırma | Browser ile dokümantasyon tara |

**Kural:** Sırayı atlama. İlk 4 adımda bulursan doğrudan uygula.
5. adımda LLM'e danıştıysan çözümü skill/reference olarak kaydet (tekrar LLM'e gitmekten kaçın).

---

## ADIM 4 — KARAR VER

Bulduğun çözümü şu kriterlerle değerlendir:

- Mevcut kodla uyumlu mu?
- Test ortamında çalışır mı?
- Yan etkisi var mı?

| Karar | Ne Zaman |
|:------|:---------|
| ✅ **UYGULA** | Her şey uyumlu, test edilebilir |
| ❌ **REDDET** | Yan etki riski, kodla uyumsuz |
| 🔄 **DAHA FAZLA ARAŞTIR** | Net değil, alternatif gerek |

---

## ADIM 5 — TEST ET

```bash
# Sandbox'ta çalıştır
pytest tests/ReYMeN_reference/acp/ -q --tb=short
```

**Kural:** 
- 5/5 test geçmeden ana koda ekleme
- Başarısızsa nedenini logla, ADIM 3'e dön
- `--collect-only` KULLANMA (pytest toplama işlemi timeoute girer). Bunun yerine `compile()` ile syntax kontrolü yap.

---

## ADIM 6 — UYGULA VE KAYDET

Test geçtiyse:

1. **Dosyaya ekle** — auth.py veya ilgili dosyaya eksik parçaları yaz
2. **Skill deposuna kaydet**:
   ```yaml
   isim: <çözümün adı>
   ne_çözdü: <problem açıklaması>
   kaynak: <nereden bulunduğu>
   test_sonucu: <kaç test geçti>
   tarih: <bugün>
   ```
3. **decisions.md güncelle** — Karar formatı:
   ```
   ## [TARİH] [KONU]
   - Sorun: ...
   - Araştırdım: ...
   - Buldum: ...
   - Karar: UYGULA / REDDET
   - Gerekçe: ...
   - Test sonucu: ...
   - Kaynak: ...
   ```
4. **Kullanıcıya rapor gönder** — Telegram'dan kısa özet

---

## Döngü Zamanlaması

| Zaman Dilimi | Mod | Açıklama |
|:-------------|:----|:---------|
| 08:00-18:00 | 🟢 Aktif | Her 20 dk'da bir döngü, aktif araştırma |
| 18:00-08:00 | 🔴 Yavaş | Sadece kritik hatalar, geniş araştırma yok |

---

## Hafıza Kuralları

- Her öğrendiğini skill deposuna yaz
- Aynı hatayı 2 kez yaparsan öncelikli görev yap
- decisions.md her kararı içermeli
- Aynı konuyu genişletiyorsan yeni kayıt AÇMA, mevcut kaydı güncelle (`kayit_guncelle`)

---

## Sınırlar (Kırmızı Çizgiler)

- Ana kodu insan onayı olmadan değiştirme (3 dk sessiz onay)
- Sandbox dışında test etme
- Güvenilmez kaynaktan kod çalıştırma
- Kaynağı belli olmayan bilgiyi uygulama
