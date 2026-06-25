# -*- coding: utf-8 -*-
"""test_turn_context.py — turn_context modulu icin testler."""

import sys
import os

# Path ayari
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from turn_context import TurnKarari, TurnContext, TurnYoneticisi


class TestTurnKarari:
    def test_varsayilan_degerler(self):
        k = TurnKarari()
        assert k.adim == 0
        assert k.eylem == ""
        assert k.arac == ""
        assert k.token_sayisi == 0
        assert k.basarili is None
        assert k.sonuc == ""

    def test_custom_degerler(self):
        k = TurnKarari(adim=3, eylem="ara", arac="web_search", token_sayisi=150)
        assert k.adim == 3
        assert k.eylem == "ara"
        assert k.arac == "web_search"
        assert k.token_sayisi == 150


class TestTurnContext:
    def test_baslangic(self):
        tc = TurnContext(tur_id=1)
        assert tc.tur_id == 1
        assert tc.kararlar == []
        assert tc._adim == 0

    def test_karar_ekle(self):
        tc = TurnContext(tur_id=1)
        k = tc.karar_ekle(eylem="oku", arac="dosya")
        assert isinstance(k, TurnKarari)
        assert k.adim == 1
        assert k.eylem == "oku"
        assert k.arac == "dosya"
        assert len(tc.kararlar) == 1

    def test_karar_ekle_artan_adim(self):
        tc = TurnContext(tur_id=1)
        tc.karar_ekle(eylem="bir")
        tc.karar_ekle(eylem="iki")
        tc.karar_ekle(eylem="uc")
        assert len(tc.kararlar) == 3
        assert [k.adim for k in tc.kararlar] == [1, 2, 3]

    def test_karar_bitir(self):
        tc = TurnContext(tur_id=1)
        tc.karar_ekle(eylem="test")
        tc.karar_bitir(basarili=True, sonuc="tamam")
        assert tc.kararlar[-1].basarili is True
        assert tc.kararlar[-1].sonuc == "tamam"

    def test_karar_bitir_bos_liste(self):
        tc = TurnContext(tur_id=1)
        # Bos listede crash etmemeli
        tc.karar_bitir(basarili=False, sonuc="hata")
        assert len(tc.kararlar) == 0

    def test_raporla(self):
        tc = TurnContext(tur_id=5)
        tc.karar_ekle(eylem="oku", arac="dosya")
        tc.karar_ekle(eylem="yaz", arac="dosya")
        tc.karar_bitir(basarili=True)

        rapor = tc.raporla()
        assert rapor["tur_id"] == 5
        assert rapor["toplam_adim"] == 2
        assert len(rapor["kararlar"]) == 2
        assert rapor["kararlar"][0]["eylem"] == "oku"
        assert rapor["kararlar"][0]["basarili"] is None  # sadece ikinci bitirildi
        assert rapor["kararlar"][1]["basarili"] is True

    def test_raporla_bos(self):
        tc = TurnContext(tur_id=0)
        rapor = tc.raporla()
        assert rapor["toplam_adim"] == 0
        assert rapor["kararlar"] == []


class TestTurnYoneticisi:
    def test_baslangic(self):
        ty = TurnYoneticisi(max_tur=5)
        assert ty.max_tur == 5
        assert ty._tur == 0

    def test_yeni_tur(self):
        ty = TurnYoneticisi(max_tur=5)
        t1 = ty.yeni_tur()
        assert isinstance(t1, TurnContext)
        assert t1.tur_id == 1

        t2 = ty.yeni_tur()
        assert t2.tur_id == 2

    def test_genel_rapor(self):
        ty = TurnYoneticisi(max_tur=10)
        ty.yeni_tur()
        ty.yeni_tur()
        ty.yeni_tur()

        rapor = ty.genel_rapor()
        assert rapor["toplam_tur"] == 3
        assert rapor["max_tur"] == 10

    def test_tur_sifirlanma(self):
        ty = TurnYoneticisi(max_tur=2)
        t = ty.yeni_tur()
        assert t.tur_id == 1
        t = ty.yeni_tur()
        assert t.tur_id == 2
        # max_tur asilmis olsa bile sayac devam eder (sinir yoklama yok)
        t = ty.yeni_tur()
        assert t.tur_id == 3
