"""Tests for reymen/sistem/health_check.py — system health checker."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestKontrol:
    """HealthChecker._kontrol() unit tests."""

    def setup_method(self):
        from reymen.sistem.health_check import HealthChecker
        self.checker = HealthChecker()

    def test_kontrol_returns_dict(self):
        result = self.checker._kontrol("test", True, "mesaj")
        assert result["ad"] == "test"
        assert result["durum"] is True
        assert result["mesaj"] == "mesaj"
        assert result["kategori"] == "genel"
        assert result["onem"] == "orta"

    def test_kontrol_kategori_onem(self):
        result = self.checker._kontrol("x", False, "y", kategori="modul", onem="kritik")
        assert result["kategori"] == "modul"
        assert result["onem"] == "kritik"
        assert result["durum"] is False

    def test_kontrol_appends_to_checks(self):
        self.checker._kontrol("a", True, "msg1")
        self.checker._kontrol("b", False, "msg2")
        assert len(self.checker._checks) == 2

    def test_kontrol_has_zaman(self):
        result = self.checker._kontrol("t", True, "m")
        assert "zaman" in result
        assert "T" in result["zaman"]  # ISO format has T


class TestFormatla:
    """HealthChecker.formatla() tests."""

    def setup_method(self):
        from reymen.sistem.health_check import HealthChecker
        self.checker = HealthChecker()

    def test_formatla_empty(self):
        # Force empty report by resetting
        self.checker._checks = []
        report = self.checker.formatla({
            "toplam": 0, "basarili": 0, "basarisiz": 0,
            "saglik_orani": "0%", "sure_saniye": 0.0,
            "kategoriler": {}, "kontroller": [],
        })
        assert "ReYMeN" in report

    def test_formatla_with_results(self):
        self.checker._checks = [
            {"ad": "mod1", "durum": True, "mesaj": "ok",
             "kategori": "modul", "onem": "kritik", "zaman": "2026-01-01T00:00:00"},
            {"ad": "mod2", "durum": False, "mesaj": "fail",
             "kategori": "modul", "onem": "orta", "zaman": "2026-01-01T00:00:00"},
        ]
        report = self.checker.formatla({
            "toplam": 2, "basarili": 1, "basarisiz": 1,
            "saglik_orani": "50%", "sure_saniye": 0.1,
            "kategoriler": {
                "modul": {
                    "basarili": 1, "basarisiz": 1,
                    "kontroller": self.checker._checks
                }
            },
            "kontroller": self.checker._checks,
        })
        assert "mod1" in report
        assert "mod2" in report
        assert "MODUL" in report

    def test_formatla_emoji_durum(self):
        self.checker._checks = [
            {"ad": "ok", "durum": True, "mesaj": "ok",
             "kategori": "test", "onem": "orta", "zaman": "2026-01-01T00:00:00"},
        ]
        report = self.checker.formatla({
            "toplam": 1, "basarili": 1, "basarisiz": 0,
            "saglik_orani": "100%", "sure_saniye": 0.0,
            "kategoriler": {"test": {"basarili": 1, "basarisiz": 0,
                           "kontroller": self.checker._checks}},
            "kontroller": self.checker._checks,
        })
        assert "✅" in report


class TestRun:
    """health_check.run() motor integration tests."""

    def setup_method(self):
        from reymen.sistem.health_check import HealthChecker
        self.checker = HealthChecker()

    def test_run_tam(self):
        from reymen.sistem.health_check import run
        result = run("tam")
        assert isinstance(result, str)
        assert "ReYMeN" in result

    def test_run_kategori_yok(self):
        from reymen.sistem.health_check import run
        result = run("kategori", kategori="")
        assert "Hata" in result

    def test_run_kategori_bulunamadi(self):
        from reymen.sistem.health_check import run
        result = run("kategori", kategori="olmayansistem")
        assert "bulunamadı" in result.lower()

    def test_run_bilinmeyen_islem(self):
        from reymen.sistem.health_check import run
        result = run("bilinmeyen")
        assert "Hata" in result


class TestSingleton:
    """_get_checker singleton test."""

    def test_singleton(self):
        from reymen.sistem.health_check import _get_checker, HealthChecker
        import reymen.sistem.health_check as mod
        mod._checker = None  # reset singleton
        c1 = _get_checker()
        c2 = _get_checker()
        assert c1 is c2
