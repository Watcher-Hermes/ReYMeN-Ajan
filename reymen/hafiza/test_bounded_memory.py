# -*- coding: utf-8 -*-
"""BoundedMemory testleri."""

import json
import os
import tempfile
import time

import pytest

from reymen.hafiza.bounded_memory import BoundedMemory


class TestBoundedMemoryBaslangic:
    """Baslangic ve yapilandirma testleri."""

    def test_varsayilan_boyut(self):
        mem = BoundedMemory()
        assert mem._max_boyut == 100
        assert len(mem._veri) == 0

    def test_ozel_boyut(self):
        mem = BoundedMemory(max_boyut=5)
        assert mem._max_boyut == 5

    def test_sifir_boyut_en_aza_cevrilir(self):
        mem = BoundedMemory(max_boyut=0)
        assert mem._max_boyut == 1

    def test_negatif_boyut_en_aza_cevrilir(self):
        mem = BoundedMemory(max_boyut=-5)
        assert mem._max_boyut == 1

    def test_kayit_yolu_ayarlanabilir(self):
        mem = BoundedMemory(kayit_yolu="/tmp/test.json")
        assert mem._kayit_yolu == "/tmp/test.json"

    def test_kapasite_bos(self):
        mem = BoundedMemory(max_boyut=10)
        assert mem.kapasite() == "0/10"

    def test_dolu_mu_bos(self):
        mem = BoundedMemory(max_boyut=10)
        assert mem.dolu_mu() is False

    def test_anahtarlar_bos(self):
        mem = BoundedMemory(max_boyut=10)
        assert mem.anahtarlar() == []

    def test_istatistik_bos(self):
        mem = BoundedMemory(max_boyut=10)
        istatistik = mem.istatistik()
        assert istatistik["ekleme"] == 0
        assert istatistik["boyut"] == 0
        assert istatistik["max_boyut"] == 10
        assert istatistik["dolu"] is False


class TestBoundedMemoryTemelIslemler:
    """Temel hatirla/unut/oku islemleri."""

    def test_hatirla_ve_oku(self):
        mem = BoundedMemory(max_boyut=10)
        sonuc = mem.hatirla("renk", "mavi")
        assert "'renk' kaydedildi" in sonuc
        assert mem.oku("renk") == "mavi"

    def test_hatirla_sayisal_deger(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("sayi", 42)
        assert mem.oku("sayi") == 42

    def test_hatirla_liste_deger(self):
        mem = BoundedMemory(max_boyut=10)
        liste = [1, 2, 3]
        mem.hatirla("liste", liste)
        assert mem.oku("liste") == liste

    def test_hatirla_dict_deger(self):
        mem = BoundedMemory(max_boyut=10)
        sozluk = {"a": 1, "b": 2}
        mem.hatirla("dict", sozluk)
        assert mem.oku("dict") == sozluk

    def test_unut_basarili(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("renk", "mavi")
        sonuc = mem.unut("renk")
        assert "'renk' silindi" in sonuc
        assert mem.oku("renk") is None

    def test_unut_olmayan_anahtar(self):
        mem = BoundedMemory(max_boyut=10)
        sonuc = mem.unut("yok")
        assert "bulunamadi" in sonuc

    def test_oku_olmayan_anahtar(self):
        mem = BoundedMemory(max_boyut=10)
        assert mem.oku("yok") is None

    def test_temizle(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        sonuc = mem.temizle()
        assert "2 oge temizlendi" in sonuc
        assert mem.anahtarlar() == []

    def test_temizle_bos(self):
        mem = BoundedMemory(max_boyut=10)
        sonuc = mem.temizle()
        assert "0 oge temizlendi" in sonuc

    def test_kapasite_artyor(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("a", 1)
        assert mem.kapasite() == "1/10"
        mem.hatirla("b", 2)
        assert mem.kapasite() == "2/10"

    def test_dolu_mu_hale_gelir(self):
        mem = BoundedMemory(max_boyut=2)
        assert mem.dolu_mu() is False
        mem.hatirla("a", 1)
        assert mem.dolu_mu() is False
        mem.hatirla("b", 2)
        assert mem.dolu_mu() is True

    def test_istatistik_guncellenir(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.oku("a")
        mem.oku("yok")
        mem.unut("b")
        ist = mem.istatistik()
        assert ist["ekleme"] == 2
        assert ist["hit"] == 1
        assert ist["miss"] == 1
        assert ist["silme"] == 1

    def test_anahtarlar_listesi(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)
        assert sorted(mem.anahtarlar()) == ["a", "b", "c"]


class TestBoundedMemoryLRU:
    """LRU atma mekanizmasi testleri."""

    def test_en_eski_oge_atilir(self):
        mem = BoundedMemory(max_boyut=3)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)
        mem.hatirla("d", 4)  # a atilmali
        assert mem.oku("a") is None
        assert mem.oku("d") == 4

    def test_lru_siralamasi_korunur(self):
        """Okuma LRU sirasini gunceller — en son okunan atilmaz."""
        mem = BoundedMemory(max_boyut=3)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)
        mem.oku("a")  # a en sona tasinir
        mem.hatirla("d", 4)  # b atilmali (en eski)
        assert mem.oku("a") == 1  # a hala duruyor
        assert mem.oku("b") is None  # b atildi

    def test_lru_guncelleme_sira_degistirmez_yine_de_at(self):
        """Guncelleme sirasinda move_to_end en sona tasir."""
        mem = BoundedMemory(max_boyut=3)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)
        mem.hatirla("a", 100)  # guncelleme, a en sona
        mem.hatirla("d", 4)  # b atilmali
        assert mem.oku("a") == 100
        assert mem.oku("b") is None

    def test_anahtar_zaten_varsa_kapasite_sayilmaz(self):
        """Varolan anahtari guncellemek kapasiteyi asmaz."""
        mem = BoundedMemory(max_boyut=2)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("a", 100)  # guncelleme, yeni oge degil
        assert mem.kapasite() == "2/2"
        assert mem.oku("a") == 100

    def test_coklu_atma(self):
        """Fazla ogeler dogru sayida atilir."""
        mem = BoundedMemory(max_boyut=2)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)  # a atilir
        sonuc = mem.hatirla("d", 4)  # b atilir
        assert "'d' kaydedildi" in sonuc
        assert mem.anahtarlar() == ["c", "d"]

    def test_istatistik_atilma_sayisi(self):
        mem = BoundedMemory(max_boyut=2)
        mem.hatirla("a", 1)
        mem.hatirla("b", 2)
        mem.hatirla("c", 3)  # a atilir -> atilma=1
        mem.hatirla("d", 4)  # b atilir -> atilma=2
        assert mem.istatistik()["atilma"] == 2

    def test_buyuk_cogunluk_atilir(self):
        """Cok fazla oge birden eklenirse dogru sayida atilir."""
        mem = BoundedMemory(max_boyut=5)
        for i in range(10):
            mem.hatirla(f"k{i}", i)
        assert len(mem.anahtarlar()) == 5
        assert mem.anahtarlar() == [f"k{5}", f"k{6}", f"k{7}", f"k{8}", f"k{9}"]


class TestBoundedMemoryStringAnahtar:
    """String olmayan anahtarlarin otomatik cevrimi."""

    def test_int_anahtar_str_cevrilir(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla(42, "deger")
        assert mem.oku("42") == "deger"

    def test_float_anahtar_str_cevrilir(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla(3.14, "pi")
        assert mem.oku("3.14") == "pi"

    def test_karma_anahtarlar(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("str", 1)
        mem.hatirla(42, 2)
        mem.hatirla(None, 3)
        assert mem.oku("str") == 1
        assert mem.oku("42") == 2
        assert mem.oku("None") == 3


class TestBoundedMemoryKalicilik:
    """JSON dosyaya kaydetme/yukleme testleri."""

    def test_otomatik_kaydet_ve_yukle(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            temp_path = f.name

        try:
            mem = BoundedMemory(max_boyut=10, kayit_yolu=temp_path)
            mem.hatirla("renk", "mavi")
            mem.hatirla("sayi", 42)

            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["veri"]["renk"] == "mavi"
            assert data["veri"]["sayi"] == 42
            assert data["istatistik"]["ekleme"] == 2
        finally:
            os.unlink(temp_path)

    def test_yukleme_dosyadan(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            temp_path = f.name
            json.dump(
                {
                    "veri": {"a": "1", "b": "2"},
                    "zaman_damgalari": {"a": time.time(), "b": time.time()},
                    "istatistik": {"ekleme": 2, "silme": 0, "atilma": 0, "hit": 0, "miss": 0},
                },
                f,
                ensure_ascii=False,
            )

        try:
            mem = BoundedMemory(max_boyut=10, kayit_yolu=temp_path)
            assert mem._yukle() is True
            assert mem.oku("a") == "1"
            assert mem.oku("b") == "2"
            assert mem.istatistik()["ekleme"] == 2
        finally:
            os.unlink(temp_path)

    def test_yukleme_bozuk_dosya(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            temp_path = f.name
            f.write("{{bozuk json")

        try:
            mem = BoundedMemory(max_boyut=10, kayit_yolu=temp_path)
            assert mem._yukle() is False
        finally:
            os.unlink(temp_path)

    def test_yukleme_olmayan_dosya(self):
        mem = BoundedMemory(max_boyut=10, kayit_yolu="/tmp/olmayan_dosya.json")
        assert mem._yukle() is False

    def test_kayit_yolu_yoksa_atla(self):
        mem = BoundedMemory(max_boyut=10)
        mem._otomatik_kaydet()  # hata vermemeli
        assert True


class TestBoundedMemoryRunFonksiyonu:
    """run() fonksiyonu testleri."""

    def test_run_hatirla(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="hatirla", anahtar="test", deger="deger")
        assert "'test' kaydedildi" in sonuc

    def test_run_unut(self):
        """run() her cagrida yeni instance olusturur — islem bazi testler bagimsiz."""
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="unut", anahtar="x")
        assert "bulunamadi" in sonuc

    def test_run_temizle(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="temizle")
        assert "0 oge temizlendi" in sonuc

    def test_run_kapasite(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="kapasite")
        assert "/100" in sonuc

    def test_run_dolu_mu(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="dolu_mu", max_boyut=1)
        assert sonuc == "Hayir" or sonuc == "Evet"

    def test_run_oku(self):
        """run() her cagrida yeni instance — hatirla state'i tasimaz."""
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="oku", anahtar="foo")
        assert "bulunamadi" in sonuc

    def test_run_anahtarlar(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="anahtarlar")
        assert sonuc == "(bos)"

    def test_run_istatistik(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="istatistik")
        data = json.loads(sonuc)
        assert "ekleme" in data
        assert "boyut" in data

    def test_run_gecersiz_islem_kapasite_dondurur(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="bilinmeyen")
        assert "/100" in sonuc

    def test_run_oku_bulunamadi(self):
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="oku", anahtar="yok")
        assert "bulunamadi" in sonuc

    def test_run_hatirla_ayri_bir_instance(self):
        """Her run cagrisi ayri instance — hatirla+oku farkli instance'da calisir."""
        from reymen.hafiza.bounded_memory import run
        sonuc = run(islem="hatirla", anahtar="test", deger="deger")
        assert "'test' kaydedildi" in sonuc
        # Ayri instance'da oku — bulamamali
        sonuc2 = run(islem="oku", anahtar="test")
        assert "bulunamadi" in sonuc2


class TestBoundedMemoryKenarDurumlar:
    """Edge case testleri."""

    def test_bos_anahtar(self):
        mem = BoundedMemory(max_boyut=10)
        sonuc = mem.hatirla("", "deger")
        assert "kaydedildi" in sonuc
        assert mem.oku("") == "deger"

    def test_unicode_anahtar(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("türkçe", "karakter")
        assert mem.oku("türkçe") == "karakter"

    def test_unicode_deger(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("test", "ğüşıöçĞÜŞİÖÇ")
        assert mem.oku("test") == "ğüşıöçĞÜŞİÖÇ"

    def test_cok_uzun_anahtar(self):
        mem = BoundedMemory(max_boyut=10)
        uzun = "a" * 10000
        mem.hatirla(uzun, "deger")
        assert mem.oku(uzun) == "deger"

    def test_none_deger_saklanabilir(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("none", None)
        assert mem.oku("none") is None

    def test_bool_deger(self):
        mem = BoundedMemory(max_boyut=10)
        mem.hatirla("dogru", True)
        mem.hatirla("yanlis", False)
        assert mem.oku("dogru") is True
        assert mem.oku("yanlis") is False

    def test_ardisik_hatirla_oku(self):
        """Cok sayida islem kararlilik testi."""
        mem = BoundedMemory(max_boyut=100)
        for i in range(100):
            mem.hatirla(f"k{i}", i * 2)
        for i in range(100):
            assert mem.oku(f"k{i}") == i * 2
        assert mem.istatistik()["ekleme"] == 100
        assert mem.istatistik()["hit"] == 100

    def test_kapasite_tam_dolu_okuma(self):
        mem = BoundedMemory(max_boyut=50)
        for i in range(50):
            mem.hatirla(f"k{i}", i)
        assert mem.dolu_mu() is True
        assert mem.anahtarlar() == [f"k{i}" for i in range(50)]
