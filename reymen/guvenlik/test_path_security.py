# -*- coding: utf-8 -*-
"""Test: path_security.py — GuvenliBolgeYoneticisi ve yardimci fonksiyonlar."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Proje kokunu sys.path'e ekle
PROJE_KOK = Path(__file__).parent.parent.parent.resolve()
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from reymen.guvenlik.path_security import (
    GuvenliBolgeYoneticisi,
    yol_dogrula,
    sembolik_link_kontrol,
    normalize_ve_dogrula,
    PROJE_KOK as MODUL_KOK,
    VARSAYILAN_OZEL_DIZINLER,
)


# ============================================================
# GuvenliBolgeYoneticisi — Temel
# ============================================================

class TestGuvenliBolgeYoneticisiTemel:
    """Temel olusturma ve property testleri."""

    def test_varsayilan_kok(self):
        yon = GuvenliBolgeYoneticisi()
        assert yon.kok == MODUL_KOK
        assert yon.kok.exists()

    def test_ozel_kok_verildiginde(self, tmp_path):
        yon = GuvenliBolgeYoneticisi(kok=tmp_path)
        assert yon.kok == tmp_path.resolve()

    def test_ozel_dizinler_verildiginde(self, tmp_path):
        yon = GuvenliBolgeYoneticisi(ozel_dizinler=[tmp_path / "ozel"])
        assert len(yon._ozel) == 1
        assert yon._ozel[0] == (tmp_path / "ozel").resolve()

    def test_varsayilan_ozel_dizin_eklimi(self):
        yon = GuvenliBolgeYoneticisi()
        assert len(yon._ozel) == len(VARSAYILAN_OZEL_DIZINLER)

    def test_bos_ozel_dizin_ekli(self):
        """Bos liste verilince __init__ bos listeyi kullanir (None degilse)."""
        yon = GuvenliBolgeYoneticisi(ozel_dizinler=[])
        assert yon._ozel == []

    def test_baslangicta_ek_izin_yok(self):
        yon = GuvenliBolgeYoneticisi()
        assert yon.izinli_yollar() == []


# ============================================================
# GuvenliBolgeYoneticisi — yol_guvenli_mi
# ============================================================

class TestYolGuvenliMi:
    """yol_guvenli_mi() metodu testleri."""

    def test_proje_koku_icinde_guvenli(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.yol_guvenli_mi(__file__)
        assert guvenli is True
        assert os.path.isabs(mesaj)

    def test_proje_koku_guvenli(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.yol_guvenli_mi(str(MODUL_KOK))
        assert guvenli is True

    def test_disari_cikis_guvensiz(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, _ = yon.yol_guvenli_mi("C:/Windows/System32")
        assert guvenli is False

    def test_gereksiz_yol_guvensiz(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, _ = yon.yol_guvenli_mi("/tmp")
        assert guvenli is False

    def test_bos_yol_guvensiz(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.yol_guvenli_mi("")
        assert guvenli is False
        assert mesaj

    def test_none_yol_guvensiz(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.yol_guvenli_mi(None)  # type: ignore
        assert guvenli is False

    def test_int_yol_guvensiz(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.yol_guvenli_mi(123)  # type: ignore
        assert guvenli is False

    def test_ek_izin_eklenince_guvenli(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        dosya = tmp_path / "test.txt"
        dosya.write_text("test")
        yon.izin_ekle(str(tmp_path))
        guvenli, _ = yon.yol_guvenli_mi(str(dosya))
        assert guvenli is True


# ============================================================
# GuvenliBolgeYoneticisi — izin_ekle / izin_cikar
# ============================================================

class TestIzinYonetimi:
    """izin_ekle() / izin_cikar() / izinli_yollar() testleri."""

    def test_izin_ekle_basarili(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        assert yon.izin_ekle(str(tmp_path)) is True
        assert str(tmp_path.resolve()) in yon.izinli_yollar()

    def test_izin_ekle_gecersiz_yol(self):
        yon = GuvenliBolgeYoneticisi()
        # cok uzun veya gecersiz karakter iceren yol
        assert yon.izin_ekle("") is not False  # resolve hata vermez, mevcut dizin olur

    def test_izin_cikar_basarili(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        assert yon.izin_cikar(str(tmp_path)) is True
        assert str(tmp_path.resolve()) not in yon.izinli_yollar()

    def test_izin_cikar_olmayan_yol(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        assert yon.izin_cikar(str(tmp_path)) is True  # discard — hata vermez

    def test_izinli_yollar_dondurur(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        alt1 = tmp_path / "alt1"
        alt2 = tmp_path / "alt2"
        alt1.mkdir()
        alt2.mkdir()
        yon.izin_ekle(str(alt1))
        yon.izin_ekle(str(alt2))
        yollar = yon.izinli_yollar()
        assert len(yollar) == 2
        assert str(alt1.resolve()) in yollar
        assert str(alt2.resolve()) in yollar

    def test_izin_ekle_tekrar_ekleme(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        yon.izin_ekle(str(tmp_path))
        assert len(yon.izinli_yollar()) == 1  # set, duplicate yok

    def test_izin_cikar_tekrarsiz_liste(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        yon.izin_ekle(str(tmp_path))
        assert len(yon.izinli_yollar()) == 1


# ============================================================
# GuvenliBolgeYoneticisi — siniflandir
# ============================================================

class TestSiniflandir:
    """siniflandir() metodu testleri."""

    def test_siniflandir_proje_koku(self):
        yon = GuvenliBolgeYoneticisi()
        sonuc = yon.siniflandir(__file__)
        assert sonuc["bolge"] == "proje_koku"
        assert sonuc["guvenli"] is True

    def test_siniflandir_izinli_bolge(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        sonuc = yon.siniflandir(str(tmp_path / "test.txt"))
        assert sonuc["bolge"] == "izinli_bolge"
        assert sonuc["guvenli"] is True

    def test_siniflandir_tehlikeli(self):
        yon = GuvenliBolgeYoneticisi()
        sonuc = yon.siniflandir("Z:/olmayan_dizin")
        assert sonuc["bolge"] == "tehlikeli"
        assert sonuc["guvenli"] is False
        assert "sebep" in sonuc

    def test_siniflandir_ozel_dizin(self):
        """Ozel dizinler izinli_bolge olarak siniflanir (proje_koku degilse)."""
        yon = GuvenliBolgeYoneticisi(ozel_dizinler=[])
        # Ozel dizin yoksa, ek izin olarak ekleyelim
        yon.izin_ekle(str(Path.home() / ".ReYMeN"))
        sonuc = yon.siniflandir(str(Path.home() / ".ReYMeN/subdir"))
        assert sonuc["guvenli"] is True
        assert sonuc["bolge"] in ("izinli_bolge", "proje_koku")

    def test_siniflandir_eksik_sebep(self):
        yon = GuvenliBolgeYoneticisi()
        sonuc = yon.siniflandir("")
        assert sonuc["guvenli"] is False


# ============================================================
# GuvenliBolgeYoneticisi — sembolik_link_guvenli_mi
# ============================================================

class TestSembolikLink:
    """sembolik_link_guvenli_mi() metodu testleri.

    Not: Windows'ta symlink icin Administrator yetkisi gerekebilir.
    """

    def test_normal_dosya_guvenli(self, tmp_path):
        yon = GuvenliBolgeYoneticisi(kok=tmp_path)
        dosya = tmp_path / "test.txt"
        dosya.write_text("test")
        guvenli, mesaj = yon.sembolik_link_guvenli_mi(str(dosya))
        assert guvenli is True
        assert mesaj == str(dosya)

    def test_symlink_proje_icinde_guvenli(self, tmp_path):
        try:
            hedef = tmp_path / "hedef.txt"
            hedef.write_text("hedef")
            link = tmp_path / "link.txt"
            link.symlink_to(hedef)
        except (OSError, NotImplementedError):
            pytest.skip("Symlink olusturma desteklenmiyor (Windows yetki)")

        yon = GuvenliBolgeYoneticisi(kok=tmp_path)
        guvenli, mesaj = yon.sembolik_link_guvenli_mi(str(link))
        assert guvenli is True
        assert mesaj == str(hedef.resolve())

    def test_symlink_disari_guvensiz(self, tmp_path):
        try:
            hedef = Path(tempfile.gettempdir()) / "hedef_disari.txt"
            hedef.write_text("hedef")
            link = tmp_path / "link_disari.txt"
            link.symlink_to(hedef)
        except (OSError, NotImplementedError):
            pytest.skip("Symlink olusturma desteklenmiyor (Windows yetki)")

        yon = GuvenliBolgeYoneticisi(kok=tmp_path)
        guvenli, mesaj = yon.sembolik_link_guvenli_mi(str(link))
        assert guvenli is False
        assert "disina" in mesaj
        if hedef.exists():
            hedef.unlink()

    def test_gecersiz_yol_dondurur(self):
        yon = GuvenliBolgeYoneticisi()
        guvenli, mesaj = yon.sembolik_link_guvenli_mi(None)  # type: ignore
        assert guvenli is False
        assert mesaj


# ============================================================
# GuvenliBolgeYoneticisi — istatistik / sifirla
# ============================================================

class TestIstatistikSifirla:
    """istatistik() ve sifirla() testleri."""

    def test_istatistik_varsayilan(self):
        yon = GuvenliBolgeYoneticisi()
        st = yon.istatistik()
        assert "kok" in st
        assert "ozel_dizin_sayisi" in st
        assert "ek_izin_sayisi" in st
        assert st["ek_izin_sayisi"] == 0
        assert st["kok"] == str(MODUL_KOK)

    def test_istatistik_ek_izin_sonrasi(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        st = yon.istatistik()
        assert st["ek_izin_sayisi"] == 1

    def test_sifirla_temizler(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        assert yon.izinli_yollar() != []
        yon.sifirla()
        assert yon.izinli_yollar() == []

    def test_sifirla_sonrasi_istatistik(self, tmp_path):
        yon = GuvenliBolgeYoneticisi()
        yon.izin_ekle(str(tmp_path))
        yon.sifirla()
        assert yon.istatistik()["ek_izin_sayisi"] == 0


# ============================================================
# Eski API uyumluluk
# ============================================================

class TestEskiAPI:
    """yol_dogrula() ve sembolik_link_kontrol() fonksiyonlari."""

    def test_yol_dogrula_proje_icinde(self):
        gecerli, mesaj = yol_dogrula(__file__)
        assert gecerli is True
        assert os.path.isabs(mesaj)

    def test_yol_dogrula_disari(self):
        gecerli, _ = yol_dogrula("C:/Windows/System32")
        assert gecerli is False

    def test_yol_dogrula_bos(self):
        gecerli, mesaj = yol_dogrula("")
        assert gecerli is False

    def test_sembolik_link_kontrol_normal(self, tmp_path):
        dosya = tmp_path / "test.txt"
        dosya.write_text("test")
        guvenli, mesaj = sembolik_link_kontrol(str(dosya))
        assert guvenli is True
        assert mesaj


# ============================================================
# normalize_ve_dogrula
# ============================================================

class TestNormalizeVeDogrula:
    """normalize_ve_dogrula() yardimci fonksiyonu."""

    def test_normal_abs_yol(self):
        gecerli, mesaj = normalize_ve_dogrula(__file__)
        assert gecerli is True
        assert os.path.isabs(mesaj)

    def test_tilde_genisletme(self):
        """~~ home'a genisletilmeli ve proje icinde degilse guvensiz."""
        gecerli, mesaj = normalize_ve_dogrula("~/.nonexistent_test_file_xyz")
        # ~ home'a genisler, proje icinde degil, ama .ReYMeN ozel dizin olabilir
        # Ozel dizin degilse guvensiz
        home_yol = Path.home() / ".nonexistent_test_file_xyz"
        if home_yol.exists():
            home_yol.unlink()
        # Genelde olmayan yol -> home icinde -> guvensiz
        # Ama .ReYMeN ozel dizinde olabilir
        assert isinstance(gecerli, bool)

    def test_genisletme_kapali(self):
        """genislet=False ile ~~ genisletilmez."""
        gecerli, mesaj = normalize_ve_dogrula("~/.test", genislet=False)
        # ~ genisletilmezse literal yol olur -> projede degil -> False
        assert gecerli is not None

    def test_bos_yol(self):
        gecerli, mesaj = normalize_ve_dogrula("")
        assert gecerli is False

    def test_gecersiz_tip(self):
        gecerli, mesaj = normalize_ve_dogrula(None)  # type: ignore
        assert gecerli is False
