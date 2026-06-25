# Sessiz Hata Yutma (Silent Error Swallowing)

## Tanım

`try/except` bloğunda bir hata yakalanır ama loglanmaz, yükseltilmez, kullanıcıya bildirilmez.
Sonuç: kod "çalışıyor" görünür ama aslında kritik bir adım atlanmıştır.

## Gerçek Dünya Örneği (ReYMeN conversation_loop.py)

```python
# ❌ BUG: sonuc dict'i web aramasından SONRA tanımlanıyor
web_sonucu = ""
try:
    # ... web araması yapılıyor ...
    sonuc["yanit"] = web_sonucu  # ← NameError: 'sonuc' is not defined
    return sonuc
except Exception as _we:
    log.warning(f"Web arama hatasi: {_we}")  # ← NameError burada yakalanıyor
    # Ama "web arama hatası" olarak loglanıyor — gerçek hata gizleniyor!

# sonuc dict'i 20 satır sonra tanımlanıyor:
sonuc = {"task_id": task_id, "basarili": False, ...}
```

**Sonuç:** Web araması hiç yapılmamış gibi davranılıyor. LLM eğitim verisinden cevap veriyor.

## Tespit Edici İşaretler

1. `except Exception: pass` — en tehlikeli
2. `except Exception as e: log.warning(...)` — hata loglanıyor ama yükseltilmiyor
3. `try` bloğunda birden fazla bağımsız işlem var
4. `except` bloğunda hata mesajı genel ("bir hata oluştu")
5. Değişken `try` bloğundan ÖNCE tanımlanmamış

## Düzeltme Şablonu

```python
# ✅ DOĞRU: 1) Önce tanımla, 2) Spesifik hata yakala, 3) Log + yükselt

sonuc = {"task_id": task_id, "basarili": False, "yanit": None}  # ÖNCE tanımla

try:
    web_sonucu = web_search_ve_ozetle(hedef)
    sonuc["yanit"] = web_sonucu
    sonuc["basarili"] = True
except ImportError as e:
    log.error(f"Web modulu bulunamadi: {e}")  # Spesifik hata
    raise  # Yükselt — sessizce yutma
except ConnectionError as e:
    log.error(f"Web arama baglanti hatasi: {e}")
    # Bu durumda LLM'e fallback yap — ama bilinçli olarak
except Exception as e:
    log.error(f"Beklenmeyen web arama hatasi: {type(e).__name__}: {e}")
    raise
```

## Kontrol Listesi

Kod incelerken şu soruları sor:

- [ ] `try` bloğundaki her değişken `try`'dan ÖNCE tanımlı mı?
- [ ] `except` bloğu hata türünü spesifik mi yakalıyor? (`Exception` değil)
- [ ] Hata loglanıyor mu? (log.warning/error)
- [ ] Hata yükseltiliyor mu? (raise) yoksa bilinçli mi yutuluyor?
- [ ] `except: pass` var mı? → EN TEHLİKELİ
- [ ] `try` bloğunda birden fazla bağımsız işlem var mı? → Ayrı try'lara böl
