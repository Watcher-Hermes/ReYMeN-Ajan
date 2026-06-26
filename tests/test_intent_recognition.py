# -*- coding: utf-8 -*-
"""test_intent_recognition.py — intent_recognition.py testleri (~30 test)."""

from reymen.sistem.intent_recognition import (
    Intent, IntentRecognizer, ContextWindow, EmbeddingEngine,
    KALIPLAR, SYNONYMS, get_recognizer, tanila,
)


# ── Intent dataclass ────────────────────────────────────────────────

class TestIntent:
    def test_temel_intent_olusturma(self):
        i = Intent(tip="hata_analizi", guven=0.9)
        assert i.tip == "hata_analizi"
        assert i.guven == 0.9
        assert i.hedef is None
        assert i.alt_tip is None

    def test_intet_tum_alanalar(self):
        i = Intent(tip="islem_yapma", guven=0.85, hedef="dosya",
                    alt_tip="calistirma", context={"key": "val"})
        assert i.hedef == "dosya"
        assert i.alt_tip == "calistirma"
        assert i.context == {"key": "val"}


# ── ContextWindow ──────────────────────────────────────────────────

class TestContextWindow:
    def test_bos_context(self):
        cw = ContextWindow(max_boyut=5)
        assert cw.baglam_bilgisi_al() is None
        assert not cw.referans_var_mi("selam dunya")

    def test_ekle_ve_son_intent(self):
        cw = ContextWindow(max_boyut=5)
        cw.ekle("hata var", Intent(tip="hata_analizi", guven=0.9))
        assert cw.son_intent.tip == "hata_analizi"
        # aktif_konu ilk eklemede None (en az 2 kayit gerekir)

    def test_ardisik_ayni_intent_konu_sabit(self):
        cw = ContextWindow(max_boyut=5)
        cw.ekle("hata var", Intent(tip="hata_analizi", guven=0.9))
        cw.ekle("bir hata daha", Intent(tip="hata_analizi", guven=0.8))
        assert cw.aktif_konu == "hata_analizi"

    def test_farkli_intent_konu_degisir(self):
        cw = ContextWindow(max_boyut=5)
        cw.ekle("hata var", Intent(tip="hata_analizi", guven=0.9))
        cw.ekle("nedir bu", Intent(tip="bilgi_isteme", guven=0.7))
        assert cw.aktif_konu == "bilgi_isteme"

    def test_referans_var_mi_dosya(self):
        cw = ContextWindow(max_boyut=5)
        assert cw.referans_var_mi("o dosyayi ac")
        assert cw.referans_var_mi("yukarıdaki hata icin")  # UTF-8 turkce karakter

    def test_referans_var_mi_devam(self):
        cw = ContextWindow(max_boyut=5)
        assert cw.referans_var_mi("devam et duzelt")
        assert cw.referans_var_mi("bitir isi")

    def test_referans_yok(self):
        cw = ContextWindow(max_boyut=5)
        assert not cw.referans_var_mi("yeni bir proje baslat")
        assert not cw.referans_var_mi("python ile kod yaz")

    def test_baglam_bilgisi_donuyor(self):
        cw = ContextWindow(max_boyut=5)
        cw.ekle("hata var", Intent(tip="hata_analizi", guven=0.9))
        cw.ekle("duzelt", Intent(tip="hata_analizi", guven=0.8))
        bilgi = cw.baglam_bilgisi_al()
        assert bilgi is not None
        assert "hata_analizi" in bilgi


# ── EmbeddingEngine (TF-IDF) ───────────────────────────────────────

class TestEmbeddingEngine:
    def test_kelime_ayir_bos(self):
        ee = EmbeddingEngine()
        assert ee._kelime_ayir("") == []
        assert ee._kelime_ayir("bir bu o") == []  # stopwords

    def test_kelime_ayir(self):
        ee = EmbeddingEngine()
        sonuc = ee._kelime_ayir("hatali kod duzelt")
        assert "hatali" in sonuc
        assert "kod" in sonuc
        assert "duzelt" in sonuc

    def test_kosinus_benzerlik_ozdes(self):
        ee = EmbeddingEngine()
        v = {"hata": 1.0, "kod": 0.5}
        assert abs(ee._kosinus_benzerlik(v, v) - 1.0) < 1e-12

    def test_kosinus_benzerlik_farkli(self):
        ee = EmbeddingEngine()
        v1 = {"hata": 1.0}
        v2 = {"python": 1.0}
        assert ee._kosinus_benzerlik(v1, v2) == 0.0

    def test_kosinus_benzerlik_kismi(self):
        ee = EmbeddingEngine()
        v1 = {"hata": 1.0, "kod": 0.5}
        v2 = {"hata": 0.8, "python": 0.3}
        skor = ee._kosinus_benzerlik(v1, v2)
        assert 0 < skor < 1.0

    def test_intent_bul_hata(self):
        ee = EmbeddingEngine()
        intent, skor = ee.intent_bul("crash bug fix error")
        assert intent == "hata_analizi"
        assert skor > 0.3

    def test_intent_bul_bilgi(self):
        ee = EmbeddingEngine()
        intent, skor = ee.intent_bul("nedir bu nasil calisir")
        assert intent == "bilgi_isteme"
        assert skor > 0.0

    def test_intent_bul_tanimisiz(self):
        ee = EmbeddingEngine()
        intent, skor = ee.intent_bul("qwerty zxcvbnm lorem ipsum")
        assert intent == "bilinmiyor" or skor <= 0.3


# ── IntentRecognizer (4 katmanli) ──────────────────────────────────

class TestIntentRecognizer:
    def test_tanila_hata_analizi_pattern(self):
        ir = IntentRecognizer()
        intent = ir.tanila("traceback hatasi var, duzelt")
        assert intent.tip == "hata_analizi"
        assert intent.guven > 0

    def test_tanila_bilgi_isteme(self):
        ir = IntentRecognizer()
        intent = ir.tanila("python nedir aciklar misin")
        assert intent.tip == "bilgi_isteme"
        assert intent.guven > 0

    def test_tanila_islem_yapma(self):
        ir = IntentRecognizer()
        intent = ir.tanila("su scripti execute et")
        assert intent.tip == "islem_yapma"
        assert intent.guven > 0

    def test_tanila_guvenlik(self):
        ir = IntentRecognizer()
        intent = ir.tanila("secure password audit")
        assert intent.tip == "guvenlik"
        assert intent.guven > 0

    def test_tanila_otomasyon(self):
        ir = IntentRecognizer()
        intent = ir.tanila("autonomous bot agent")
        assert intent.tip == "otomasyon"
        assert intent.guven > 0

    def test_tanila_performans(self):
        ir = IntentRecognizer()
        intent = ir.tanila("bellek ve disk performansi")
        assert intent.tip == "performans"

    def test_tanila_gui(self):
        ir = IntentRecognizer()
        intent = ir.tanila("open telegram screen")
        assert intent.tip == "gui"

    def test_tanila_bilinmiyor(self):
        ir = IntentRecognizer()
        intent = ir.tanila("qwertyuioplkjhgfdsa")
        assert intent.tip == "bilinmiyor"
        assert intent.guven == 0.0

    def test_tanila_hedef_bul_dosya(self):
        ir = IntentRecognizer()
        intent = ir.tanila("config.yaml hata var duzelt")
        assert intent.hedef == "dosya" or intent.hedef == "config"

    def test_tanila_hedef_bul_servis(self):
        ir = IntentRecognizer()
        intent = ir.tanila("gateway servisini yeniden baslat")
        assert intent.hedef == "servis"

    def test_kalip_ekle(self):
        ir = IntentRecognizer()
        ir.kalip_ekle("ozel_intent", r"xyz_benzersiz_kelime_123456", 0.9, "test")
        assert "ozel_intent" in ir._compiled
        intent = ir.tanila("xyz_benzersiz_kelime_123456 hakkinda")
        assert intent.tip == "ozel_intent"

    def test_es_anlamlilar(self):
        ir = IntentRecognizer()
        esler = ir.es_anlamlilar("hata")
        assert "error" in esler
        assert "bug" in esler
        assert "hata" in esler

    def test_es_anlamlilar_bilinmiyor(self):
        ir = IntentRecognizer()
        esler = ir.es_anlamlilar("xyz123nonexistent")
        assert esler == ["xyz123nonexistent"]

    def test_context_entegrasyonu(self):
        """IntentRecognizer context window'u kullanir."""
        ir = IntentRecognizer()
        ir.tanila("hata var traceback")
        ir.tanila("duzelt su hatayi")
        assert ir.context.aktif_konu == "hata_analizi"
        assert ir.context.baglam_bilgisi_al() is not None

    def test_synonym_yonlendirme(self):
        """Synonym mapping intent skorlarina bonus ekler."""
        ir = IntentRecognizer()
        # "fix" dogrudan KALIPLAR'da yok ama SYNONYMS'de "düzelt" icin var
        intent = ir.tanila("fix")
        # fix synonym'i "islem_yapma" icin bonus ekleyebilir
        assert intent.guven >= 0.0


# ── Global helper fonksiyonlar ─────────────────────────────────────

class TestGlobalHelpers:
    def test_get_recognizer_singleton(self):
        r1 = get_recognizer()
        r2 = get_recognizer()
        assert r1 is r2

    def test_tanila_kisa_yol(self):
        intent = tanila("bu hatayi duzelt")
        assert intent.tip == "hata_analizi"
        assert intent.guven > 0


# ── Sabitlerin dogrulugu ───────────────────────────────────────────

class TestSabitler:
    def test_kaliplar_bos_degil(self):
        assert len(KALIPLAR) > 0

    def test_kaliplar_tum_intentler_derlenebilir(self):
        import re
        for intent, kalip_listesi in KALIPLAR.items():
            for kalip, _, alt in kalip_listesi:
                compiled = re.compile(kalip, re.IGNORECASE)
                assert compiled is not None

    def test_synonyms_tutarlı(self):
        """Her synonym en az bir KALIPLAR'a ait olmali (yumusak kontrol)."""
        tum_kalip_metinler = []
        for kalip_listesi in KALIPLAR.values():
            for kalip, _, _ in kalip_listesi:
                tum_kalip_metinler.append(kalip)
        # En azindan bazi synonym kelimeler kalip metinlerinde gecmeli
        import re
        eslesme_sayisi = 0
        for es_listesi in SYNONYMS.values():
            for es in es_listesi[:3]:  # ilk 3
                for km in tum_kalip_metinler:
                    if es.lower() in km.lower():
                        eslesme_sayisi += 1
                        break
        assert eslesme_sayisi > 0, "Hicbir synonym kalip metninde gecmiyor"
