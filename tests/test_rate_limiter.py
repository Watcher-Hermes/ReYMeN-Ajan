# -*- coding: utf-8 -*-
"""Test suite for reymen.sistem.rate_limiter — sliding-window + token budget."""
import os
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reymen" / "sistem"))

# ── RateLimiter ──────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
_RATE_LIMITER_PATH = str(ROOT / "reymen" / "sistem" / "rate_limiter.py")

import importlib.util as _iu
def _import_rl():
    _spec = _iu.spec_from_file_location("rate_limiter_rl", _RATE_LIMITER_PATH)
    _mod = _iu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    return _mod
_rl = _import_rl()

class TestRateLimiter:
    def setup_method(self):
        self.rl = _rl.RateLimiter(rpm=5, pencere=10)

    def test_ilk_istek_izin(self):
        assert self.rl.izin_var_mi("test") is True

    def test_5_istek_sonra_limit_doldu(self):
        for _ in range(5):
            self.rl.kaydet("test")
        assert self.rl.izin_var_mi("test") is False

    def test_bekle_sonra_izin_acilir(self):
        rl = _rl.RateLimiter(rpm=2, pencere=1)
        rl.kaydet("fast")
        rl.kaydet("fast")
        assert rl.izin_var_mi("fast") is False
        time.sleep(1.1)
        assert rl.izin_var_mi("fast") is True

    def test_farkli_provider_bagimsiz(self):
        self.rl.kaydet("a")
        self.rl.kaydet("a")
        assert self.rl.izin_var_mi("a") is True
        assert self.rl.izin_var_mi("b") is True

    def test_durum_dogru(self):
        self.rl.kaydet("x")
        self.rl.kaydet("x")
        d = self.rl.durum("x")
        assert d["kullanilan"] == 2
        assert d["sinir"] == 5
        assert d["bos"] == 3

    def test_tum_durum(self):
        self.rl.kaydet("p1")
        self.rl.kaydet("p2")
        durumlar = self.rl.tum_durum()
        assert len(durumlar) == 2

    def test_thread_safety(self):
        rl = type(self.rl)(rpm=50, pencere=10)
        errors = []
        def worker():
            try:
                for _ in range(20):
                    rl.kaydet("shared")
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        d = rl.durum("shared")
        assert d["kullanilan"] == 80


# ── TokenBudget ──────────────────────────────────────────────────────────────

class TestTokenBudget:
    def setup_method(self):
        self.tb = _rl.TokenBudget(gunluk_sinir=100)

    def test_token_tahmin(self):
        assert _rl.TokenBudget.token_tahmin("") == 1
        assert _rl.TokenBudget.token_tahmin("hello") == 1
        assert _rl.TokenBudget.token_tahmin("hello world foo") == int(3 * 1.3)

    def test_kaydet_sayar(self):
        self.tb.kaydet("merhaba dunya test", "p")
        assert self.tb.toplam() > 0

    def test_sinir_asildimi(self):
        assert self.tb.sinir_asildimi() is False
        self.tb.kaydet("x " * 80, "p")  # ~52 token
        assert self.tb.toplam() >= 0
        # Büyük ekle
        self.tb.kaydet("word " * 200, "p")
        assert self.tb.sinir_asildimi() is True

    def test_kalan_sinirsiz(self):
        tb = _rl.TokenBudget(gunluk_sinir=0)
        tb.kaydet("test", "p")
        assert tb.kalan() == -1

    def test_kalan_sinirli(self):
        self.tb.kaydet("hello", "p")
        kalan = self.tb.kalan()
        assert 0 <= kalan <= 100

    def test_durum(self):
        self.tb.kaydet("test metin", "p")
        d = self.tb.durum()
        assert "gun" in d
        assert "harcanan" in d
        assert "sinir" in d

    def test_rapor_string(self):
        r = self.tb.rapor()
        assert isinstance(r, str)
        assert "TokenBudget" in r


# ── Helper Functions ─────────────────────────────────────────────────────────

class TestEnvHelpers:
    def test_env_int_default(self):
        assert _rl._env_int("NONEXISTENT_KEY_99999", 42) == 42

    def test_env_int_parses(self):
        os.environ["TEST_RL_INT"] = "123"
        try:
            assert _rl._env_int("TEST_RL_INT", 0) == 123
        finally:
            del os.environ["TEST_RL_INT"]

    def test_env_bool_default(self):
        assert _rl._env_bool("NONEXISTENT_KEY_BOOL", False) is False

    def test_env_bool_true(self):
        os.environ["TEST_RL_BOOL"] = "true"
        try:
            assert _rl._env_bool("TEST_RL_BOOL") is True
        finally:
            del os.environ["TEST_RL_BOOL"]


# ── Syntax Smoke ─────────────────────────────────────────────────────────────

class TestSyntax:
    def test_module_compiles(self):
        src = (ROOT / "reymen" / "sistem" / "rate_limiter.py").read_text()
        compile(src, "rate_limiter.py", "exec")
