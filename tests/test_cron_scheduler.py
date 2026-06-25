# -*- coding: utf-8 -*-
"""test_cron_scheduler.py — CronExpressionParser + CronScheduler testleri."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Project root
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from reymen.sistem.cron_scheduler import CronExpressionParser, CronScheduler


# ── CronExpressionParser ──

class TestCronExpressionParser:
    def test_her_dakika(self):
        p = CronExpressionParser("* * * * *")
        assert p.dakika == set(range(0, 60))
        assert p.saat == set(range(0, 24))

    def test_baslik_saat(self):
        p = CronExpressionParser("0 9 * * *")
        assert p.dakika == {0}
        assert p.saat == {9}

    def test_adim(self):
        p = CronExpressionParser("*/15 * * * *")
        assert p.dakika == {0, 15, 30, 45}

    def test_aralik(self):
        p = CronExpressionParser("0 0 1-5 * *")
        assert p.gun == {1, 2, 3, 4, 5}

    def test_karma(self):
        p = CronExpressionParser("0 9 * * 1,3,5")
        assert p.hafta_gunu == {1, 3, 5}

    def test_gecersiz_ifade(self):
        with pytest.raises(ValueError):
            CronExpressionParser("yalniz_3_alan * *")

    def test_repr(self):
        p = CronExpressionParser("0 9 * * *")
        assert "0 9 * * *" in repr(p)

    def test_eslesiyor_her_dakika(self):
        p = CronExpressionParser("* * * * *")
        t = datetime(2026, 6, 25, 14, 30)
        assert p.eslesiyor(t) is True

    def test_eslesiyor_baslik_saat(self):
        p = CronExpressionParser("0 9 * * *")
        assert p.eslesiyor(datetime(2026, 6, 25, 9, 0)) is True
        assert p.eslesiyor(datetime(2026, 6, 25, 9, 1)) is False
        assert p.eslesiyor(datetime(2026, 6, 25, 10, 0)) is False

    def test_eslesiyor_haftaici(self):
        """0 9 * * 1-5 = Pazartesi-Cuma 09:00"""
        p = CronExpressionParser("0 9 * * 1-5")
        # 2026-06-29 = Pazartesi (weekday=0, cron_hafta_gunu=1)
        assert p.eslesiyor(datetime(2026, 6, 29, 9, 0)) is True
        # 2026-06-27 = Cumartesi (weekday=5, cron_hafta_gunu=6)
        assert p.eslesiyor(datetime(2026, 6, 27, 9, 0)) is False

    def test_eslesiyor_adim(self):
        p = CronExpressionParser("*/15 * * * *")
        assert p.eslesiyor(datetime(2026, 1, 1, 0, 0)) is True
        assert p.eslesiyor(datetime(2026, 1, 1, 0, 15)) is True
        assert p.eslesiyor(datetime(2026, 1, 1, 0, 7)) is False


# ── CronScheduler ──

@pytest.fixture
def sched(tmp_path):
    json_yolu = str(tmp_path / "cron.json")
    return CronScheduler(json_yolu=json_yolu)


@pytest.fixture
def sched_nojson():
    return CronScheduler()


class TestCronSchedulerEkle:
    def test_ekle_basarili(self, sched_nojson):
        result = sched_nojson.ekle("j1", "0 9 * * *", lambda: None)
        assert result is True

    def test_ekle_gecersiz_cron(self, sched_nojson):
        result = sched_nojson.ekle("j1", "invalid", lambda: None)
        assert result is False

    def test_listele(self, sched_nojson):
        sched_nojson.ekle("j1", "0 9 * * *", lambda: None, aciklama="test")
        liste = sched_nojson.listele()
        assert len(liste) == 1
        assert liste[0]["id"] == "j1"
        assert liste[0]["aciklama"] == "test"

    def test_bos_liste(self, sched_nojson):
        assert sched_nojson.listele() == []

    def test_sil(self, sched_nojson):
        sched_nojson.ekle("j1", "0 9 * * *", lambda: None)
        result = sched_nojson.sil("j1")
        assert result is True
        assert len(sched_nojson.listele()) == 0

    def test_sil_olmayan(self, sched_nojson):
        assert sched_nojson.sil("nonexistent") is False

    def test_json_kaydetme(self, sched, tmp_path):
        sched.ekle("j1", "0 9 * * *", lambda: None)
        json_dosya = tmp_path / "cron.json"
        assert json_dosya.exists()
        data = json.loads(json_dosya.read_text(encoding="utf-8"))
        assert "j1" in data
        assert data["j1"]["cron"] == "0 9 * * *"


class TestCronSchedulerRun:
    def test_run_listele(self, sched_nojson):
        sonuc = sched_nojson.run(action="listele")
        data = json.loads(sonuc)
        assert isinstance(data, list)

    def test_run_ekle(self, sched_nojson):
        sonuc = sched_nojson.run(action="ekle", job_id="j1",
                                  zaman="0 9 * * *", fonk=lambda: None)
        data = json.loads(sonuc)
        assert data["basarili"] is True

    def test_run_sil(self, sched_nojson):
        sched_nojson.ekle("j1", "0 9 * * *", lambda: None)
        sonuc = sched_nojson.run(action="sil", job_id="j1")
        data = json.loads(sonuc)
        assert data["basarili"] is True

    def test_run_bilinmeyen_action(self, sched_nojson):
        sonuc = sched_nojson.run(action="yanlis")
        data = json.loads(sonuc)
        assert "hata" in data


class TestCronSchedulerBaslatDurdur:
    def test_baslat_durdur(self, sched_nojson):
        assert sched_nojson.baslat() is True
        assert sched_nojson._calisiyor is True
        # Tekrar baslatmaya calis
        assert sched_nojson.baslat() is False
        assert sched_nojson.durdur() is True
        assert sched_nojson._calisiyor is False

    def test_durdur_baslamadiysa(self, sched_nojson):
        assert sched_nojson.durdur() is False


class TestCronSchedulerPersistance:
    def test_yukleme(self, tmp_path):
        json_yolu = str(tmp_path / "cron.json")
        # Ilk scheduler — job ekle
        s1 = CronScheduler(json_yolu=json_yolu)
        s1.ekle("j1", "0 9 * * *", lambda: None)
        # Yeni scheduler — ayni json'dan yuklemeli
        s2 = CronScheduler(json_yolu=json_yolu)
        liste = s2.listele()
        assert len(liste) == 1
        assert liste[0]["id"] == "j1"


class TestTekSeferlik:
    def test_tek_seferlik_sonrasi_silinir(self, sched_nojson):
        sched_nojson.ekle("j_once", "0 9 * * *", lambda: None, tek_seferlik=True)
        job = sched_nojson._jobs["j_once"]
        # Manuel calistir (thread'siz)
        sched_nojson._gorev_calistir("j_once", job)
        assert "j_once" not in sched_nojson._jobs
