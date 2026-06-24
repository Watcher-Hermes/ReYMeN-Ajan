# -*- coding: utf-8 -*-
"""tests/test_circuit_breaker.py — CircuitBreaker birim testleri.

Calistirma: python -m pytest tests/test_circuit_breaker.py -v
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_breaker import CircuitBreaker, CircuitBreakerState


# ══════════════════════════════════════════════════════════════════════════════
# Temel Durum Testleri
# ══════════════════════════════════════════════════════════════════════════════

class TestCircuitBreakerInit:

    def test_baslangic_durumu_closed(self):
        cb = CircuitBreaker()
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_baslangic_hata_sayaci_sifir(self):
        cb = CircuitBreaker()
        assert cb.ardisik_hata == 0

    def test_baslangic_son_acilma_sifir(self):
        cb = CircuitBreaker()
        assert cb.son_acilma == 0.0

    def test_esik_5(self):
        assert CircuitBreaker.ESIK == 5

    def test_bekleme_suresi_30(self):
        assert CircuitBreaker.BEKLEME_SURESI == 30

    def test_denetle_closed_none_doner(self):
        cb = CircuitBreaker()
        assert cb.denetle() is None


# ══════════════════════════════════════════════════════════════════════════════
# Hata Kaydetme Testleri
# ══════════════════════════════════════════════════════════════════════════════

class TestHataKaydet:

    def test_4_hata_open_etmez(self):
        cb = CircuitBreaker()
        for _ in range(4):
            mesaj = cb.hata_kaydet()
        assert mesaj is None
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_5_hata_circuit_acar(self):
        cb = CircuitBreaker()
        mesaj = None
        for _ in range(5):
            mesaj = cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN
        assert mesaj is not None
        assert "[CIRCUIT_BREAKER]" in mesaj

    def test_5_hata_mesaji_hata_sayisini_icerir(self):
        cb = CircuitBreaker()
        for _ in range(4):
            cb.hata_kaydet()
        mesaj = cb.hata_kaydet()
        assert "5" in mesaj

    def test_5_hata_mesaji_circuit_open_icerir(self):
        cb = CircuitBreaker()
        for _ in range(4):
            cb.hata_kaydet()
        mesaj = cb.hata_kaydet()
        assert "circuit open" in mesaj.lower() or "CIRCUIT_BREAKER" in mesaj

    def test_5_hata_son_acilma_guncellenir(self):
        cb = CircuitBreaker()
        once = time.time()
        for _ in range(5):
            cb.hata_kaydet()
        assert cb.son_acilma >= once

    def test_4_hata_sonrasi_sayac_4(self):
        cb = CircuitBreaker()
        for _ in range(4):
            cb.hata_kaydet()
        assert cb.ardisik_hata == 4

    def test_6_hata_6_sayac(self):
        cb = CircuitBreaker()
        for _ in range(6):
            cb.hata_kaydet()
        assert cb.ardisik_hata == 6


# ══════════════════════════════════════════════════════════════════════════════
# Başarı Kaydetme Testleri
# ══════════════════════════════════════════════════════════════════════════════

class TestBasariKaydet:

    def test_basari_sayaci_sifirlar(self):
        cb = CircuitBreaker()
        for _ in range(3):
            cb.hata_kaydet()
        cb.basari_kaydet()
        assert cb.ardisik_hata == 0

    def test_basari_closed_durumu_degistirmez(self):
        cb = CircuitBreaker()
        cb.basari_kaydet()
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_half_open_basari_closed_yapar(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        cb.basari_kaydet()
        assert cb.durum == CircuitBreakerState.CLOSED

    def test_half_open_basari_sayaci_sifirlar(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        cb.ardisik_hata = 5
        cb.basari_kaydet()
        assert cb.ardisik_hata == 0


# ══════════════════════════════════════════════════════════════════════════════
# Denetle Testleri (OPEN / HALF_OPEN)
# ══════════════════════════════════════════════════════════════════════════════

class TestDenetle:

    def test_open_denetle_mesaj_doner(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN
        mesaj = cb.denetle()
        assert mesaj is not None
        assert "[CIRCUIT_BREAKER]" in mesaj

    def test_open_denetle_kalan_sure_icerir(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        mesaj = cb.denetle()
        assert "s kaldi" in mesaj

    def test_open_30sn_sonra_half_open(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        # Zamanı 31sn ileri al
        cb.son_acilma = time.time() - 31
        mesaj = cb.denetle()
        assert mesaj is None
        assert cb.durum == CircuitBreakerState.HALF_OPEN

    def test_half_open_denetle_none_doner(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        assert cb.denetle() is None

    def test_half_open_hata_open_yapar(self):
        cb = CircuitBreaker()
        cb.durum = CircuitBreakerState.HALF_OPEN
        cb.ardisik_hata = 4  # bir hata yeterli (4+1=5 → OPEN)
        cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN

    def test_open_29sn_hala_open(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        cb.son_acilma = time.time() - 29
        mesaj = cb.denetle()
        assert mesaj is not None
        assert cb.durum == CircuitBreakerState.OPEN


# ══════════════════════════════════════════════════════════════════════════════
# Tam Durum Makinesi Döngüsü
# ══════════════════════════════════════════════════════════════════════════════

class TestDurumMakinesiDongusu:

    def test_closed_open_half_open_closed(self):
        cb = CircuitBreaker()

        # CLOSED → 5 hata → OPEN
        for _ in range(5):
            cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN

        # OPEN → 30sn → HALF_OPEN
        cb.son_acilma = time.time() - 31
        cb.denetle()
        assert cb.durum == CircuitBreakerState.HALF_OPEN

        # HALF_OPEN → basari → CLOSED
        cb.basari_kaydet()
        assert cb.durum == CircuitBreakerState.CLOSED
        assert cb.ardisik_hata == 0

    def test_closed_open_half_open_open_tekrar(self):
        cb = CircuitBreaker()

        for _ in range(5):
            cb.hata_kaydet()
        cb.son_acilma = time.time() - 31
        cb.denetle()
        assert cb.durum == CircuitBreakerState.HALF_OPEN

        # HALF_OPEN → 5 hata → OPEN tekrar
        cb.ardisik_hata = 4
        cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN

    def test_sifirla(self):
        cb = CircuitBreaker()
        for _ in range(5):
            cb.hata_kaydet()
        assert cb.durum == CircuitBreakerState.OPEN
        cb.sifirla()
        assert cb.durum == CircuitBreakerState.CLOSED
        assert cb.ardisik_hata == 0
        assert cb.son_acilma == 0.0
        assert cb.denetle() is None

    def test_durum_bilgisi_dict(self):
        cb = CircuitBreaker()
        bilgi = cb.durum_bilgisi()
        assert "durum" in bilgi
        assert "ardisik_hata" in bilgi
        assert "son_acilma" in bilgi


# ══════════════════════════════════════════════════════════════════════════════
# Katman4Kanca Entegrasyon Testleri
# ══════════════════════════════════════════════════════════════════════════════

class TestKatman4KancaCircuitBreaker:

    def test_katman4_cb_nitelik(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        assert hasattr(k4, "_cb")
        assert k4._cb is not None

    def test_katman4_cb_baslangic_closed(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        assert k4._cb.durum == CircuitBreakerState.CLOSED

    def test_katman4_hata_bildir_cb_arttirir(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        for _ in range(4):
            k4.hata_bildir("task_01")
        assert k4._cb.ardisik_hata == 4

    def test_katman4_hata_bildir_5_open(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        for _ in range(5):
            k4.hata_bildir("task_01")
        assert k4._cb.durum == CircuitBreakerState.OPEN

    def test_katman4_denetle_open_bloke(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        for _ in range(5):
            k4.hata_bildir("task_01")
        # Simdi denetle CIRCUIT_BREAKER mesaji donmeli
        mesaj = k4.denetle("task_02", "DOSYA_OKU")
        assert mesaj is not None
        assert "[CIRCUIT_BREAKER]" in mesaj

    def test_katman4_basari_bildir_sayaci_sifirlar(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        for _ in range(3):
            k4.hata_bildir("task_01")
        k4.basari_bildir("task_01")
        assert k4._cb.ardisik_hata == 0

    def test_katman4_istatistik_cb_bilgisi(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        ist = k4.istatistik()
        assert "circuit_breaker" in ist
        assert "durum" in ist["circuit_breaker"]

    def test_katman4_cb_sifirla(self, tmp_path):
        from steering_loop import Katman4Kanca
        k4 = Katman4Kanca(db_path=str(tmp_path / "cb_test.db"))
        for _ in range(5):
            k4.hata_bildir("task_01")
        k4.circuit_breaker_sifirla()
        assert k4._cb.durum == CircuitBreakerState.CLOSED
        assert k4.denetle("task_02", "DOSYA_OKU") is None
