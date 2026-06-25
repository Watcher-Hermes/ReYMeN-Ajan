# Memory Bank — ReYMeN Değişiklik Kaydı

Bu dosya, ReYMeN projesinde yapılan her değişikliğin özetini tutar.
**Model değişimlerinde, oturum atlamalarında devamlılık bu dosya ile sağlanır.**
Her oturum BAŞINDA okunur, SONUNDA güncellenir.

## FORMAT

```
### TARİH — BAŞLIK

**Yapılan:**
- [dosya:satır] değişiklik açıklaması

**Karar (3 soru):**
1. Ne yaptın?
2. Neden?
3. Alternatif?

**Durum:** ✅ TAMAM / 🔧 DEVAM EDİYOR / ⛔ İPTAL
```

---

### 2026-06-25 — 3 Kritik MD Dosyası Doldurma

**Yapılan:**
- `AI Guidelines.md` — proje yapısı, akış diyagramı, 10 kural eklendi
- `Memory Bank.md` — format şablonu, ilk kayıt eklendi (bu dosya)
- `Proje Amaçları.md` — vizyon, hedefler, risk matrisi, kısıtlar eklendi

**Karar:**
1. **Ne yaptın?** 3 MD dosyasını projeye özgü akışla doldurdu.
2. **Neden?** Generic kurallar değil, ReYMeN'in gerçek dosya yapısına ve modüllerine göre çalışma talimatı gerek.
3. **Alternatif?** AGENTS.md'ye tek dosyada birleştirilebilirdi ama ayrı dosyalar daha modüler.

**Durum:** ✅ TAMAM

---

### 2026-06-25 — Halüsinasyon + Drift Fix (Önceki Oturum)

**Yapılan:**
- `conversation_loop.py:527-539` — canlı veri bypass (once_hafiza atlanıyor)
- `once_hafiza.py:509,529` — JSON truncation fix (200→2000)
- `ajan_suru.py:133-173` — döngü kırıcı (MAX=6, _maks_tur=2)
- `auto_web_search.py` — cache TTL (300s), _sonuc_cache
- `beyin.py` — frequency_penalty=0.8, _tekrar_temizle()
- `reymen_agent.py` — multi-provider fallback

**Karar:**
1. **Ne yaptın?** 6 dosyada halüsinasyon/drift/loop fix.
2. **Neden?** "Altın ons fiyatı" sorgusu cache miss → drift → sonsuz döngü.
3. **Alternatif?** LLM timeout artırılabilirdi ama döngü kırıcı daha güvenli.

**Durum:** ✅ TAMAM

---

### 2026-06-25 — Harem Altın Canlı Veri Çekme

**Yapılan:**
- `web_extract` ile haremaltin.com canlı piyasa verileri çekildi
- ONS: $3.988, Gram: 6.017 ₺, Çeyrek: 9.886 ₺ tespit edildi

**Durum:** ✅ TAMAM

---

### 2026-06-25 — Playwright Kurulumu

**Yapılan:**
- `kur_playwright.py` scripti yazıldı (hata düzeltildi: `name` → `__name__`)
- Playwright kurulu, chromium indirildi, test geçti

**Durum:** ✅ TAMAM
