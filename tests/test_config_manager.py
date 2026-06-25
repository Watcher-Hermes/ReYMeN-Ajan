# -*- coding: utf-8 -*-
"""
test_config_manager.py — config_manager.py kapsamlı test.
"""
import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Yardımcı ──────────────────────────────────────────────────────────────

def _tmp_config():
    """Geçici config dosyasıyla Config nesnesi oluştur."""
    d = tempfile.mkdtemp()
    cfg_path = os.path.join(d, "test_config.json")
    return cfg_path, d


# ── Test Classes ───────────────────────────────────────────────────────────

class TestVarsayilanlar:
    """Varsayılan değerler doğru yükleniyor mu?"""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_model_varsayilan(self):
        assert self.cfg.get("model") == "mimo-v2.5-pro"

    def test_provider_varsayilan(self):
        assert self.cfg.get("provider") == "xiaomi"

    def test_temperature_varsayilan(self):
        assert self.cfg.get("temperature") == 0.7

    def test_max_tokens_varsayilan(self):
        assert self.cfg.get("max_tokens") == 4096

    def test_max_iterations_varsayilan(self):
        assert self.cfg.get("max_iterations") == 90

    def test_circuit_breaker_varsayilan(self):
        assert self.cfg.get("circuit_breaker_threshold") == 3
        assert self.cfg.get("circuit_breaker_permanent") is True

    def test_memory_max_chars(self):
        assert self.cfg.get("memory_max_chars") == 2200

    def test_varsayilan_sayisi(self):
        """En az 30 varsayılan anahtar tanımlı olmalı."""
        assert len(self.cfg.VARSAYILAN) >= 30


class TestGetSet:
    """Basit ve iç içe get/set."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_get_basit(self):
        assert self.cfg.get("model") is not None

    def test_get_yok(self):
        assert self.cfg.get("nonexistent") is None
        assert self.cfg.get("nonexistent", "default") == "default"

    def test_set_basit(self):
        self.cfg.set("model", "test-model")
        assert self.cfg.get("model") == "test-model"

    def test_set_ic_ice(self):
        self.cfg.set("api_keys.test", "abc123")
        assert self.cfg.get("api_keys.test") == "abc123"

    def test_set_derin_ic_ice(self):
        self.cfg.set("a.b.c.d", "deep")
        assert self.cfg.get("a.b.c.d") == "deep"


class TestDerinBirlestir:
    """Sözlük birleştirme (deep merge)."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_birlestir_basit(self):
        hedef = {"a": 1, "b": 2}
        self.cfg._derin_birlestir(hedef, {"b": 3, "c": 4})
        assert hedef == {"a": 1, "b": 3, "c": 4}

    def test_birlestir_nested(self):
        hedef = {"a": {"x": 1, "y": 2}}
        self.cfg._derin_birlestir(hedef, {"a": {"y": 99, "z": 3}})
        assert hedef == {"a": {"x": 1, "y": 99, "z": 3}}

    def test_birlestir_override_tip(self):
        """dict→str override doğru çalışmalı."""
        hedef = {"a": {"x": 1}}
        self.cfg._derin_birlestir(hedef, {"a": "not-a-dict"})
        assert hedef["a"] == "not-a-dict"


class TestNestedAccess:
    """Noktalı anahtar ile erişim."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_get_nested_varolan(self):
        val = self.cfg._get_nested("model")
        assert val == "mimo-v2.5-pro"

    def test_get_nested_yok(self):
        assert self.cfg._get_nested("nonexistent.path", "def") == "def"

    def test_set_nested_yeni_dict(self):
        self.cfg._set_nested("new.key", "val")
        assert self.cfg._data["new"]["key"] == "val"

    def test_set_nested_mevcut_dict(self):
        self.cfg._set_nested("model", "override")
        assert self.cfg._data["model"] == "override"


class TestDosyaPersistance:
    """Dosyaya kaydetme ve yükleme."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config as Cfg
        self._Config = Cfg
        self.cfg_path, self._dir = _tmp_config()

    def teardown_method(self):
        for f in Path(self._dir).glob("*"):
            f.unlink()
        os.rmdir(self._dir)

    def test_kaydet_ve_yukle(self):
        cfg1 = self._Config(config_path=self.cfg_path)
        cfg1.set("model", "persist-test")
        cfg1._kaydet()

        cfg2 = self._Config(config_path=self.cfg_path)
        assert cfg2.get("model") == "persist-test"

    def test_bozuk_dosya(self):
        Path(self.cfg_path).write_text("NOT JSON!!!", encoding="utf-8")
        cfg = self._Config(config_path=self.cfg_path)
        # Varsayılanlar yüklenmeli
        assert cfg.get("model") == "mimo-v2.5-pro"


class TestReset:
    """Reset fonksiyonu."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_reset_degerleri(self):
        self.cfg.set("model", "changed")
        assert self.cfg.get("model") == "changed"
        self.cfg.reset()
        assert self.cfg.get("model") == "mimo-v2.5-pro"


class TestFormatla:
    """formatla() çıkış formatı."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()
        self.cfg = Config(config_path=self.cfg_path)

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_formatla_baslik(self):
        cikti = self.cfg.formatla()
        assert "Yapılandırma" in cikti

    def test_formatla_icerik(self):
        cikti = self.cfg.formatla()
        assert "model" in cikti
        assert "mimo-v2.5-pro" in cikti


class TestRunMotorEntegrasyonu:
    """run() motor entegrasyon fonksiyonu."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config, get_config
        self.cfg_path, self._dir = _tmp_config()
        # Reset singleton
        import reymen.sistem.config_manager as cm
        cm._cfg = None
        self.cfg = Config(config_path=self.cfg_path)
        cm._cfg = self.cfg

    def teardown_method(self):
        import reymen.sistem.config_manager as cm
        cm._cfg = None
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_run_oku(self):
        from reymen.sistem.config_manager import run
        sonuc = run("oku", "model")
        assert "mimo-v2.5-pro" in sonuc

    def test_run_oku_tum(self):
        from reymen.sistem.config_manager import run
        sonuc = run("oku")
        assert "Yapılandırma" in sonuc

    def test_run_oku_yok(self):
        from reymen.sistem.config_manager import run
        sonuc = run("oku", "nonexistent_key_xyz")
        assert "Hata" in sonuc

    def test_run_ayarla_bool(self):
        from reymen.sistem.config_manager import run
        sonuc = run("ayarla", "security_strict", "false")
        assert "✅" in sonuc
        assert self.cfg.get("security_strict") is False

    def test_run_ayarla_int(self):
        from reymen.sistem.config_manager import run
        sonuc = run("ayarla", "max_tokens", "8192")
        assert "✅" in sonuc
        assert self.cfg.get("max_tokens") == 8192

    def test_run_ayarla_float(self):
        from reymen.sistem.config_manager import run
        sonuc = run("ayarla", "temperature", "0.5")
        assert "✅" in sonuc
        assert self.cfg.get("temperature") == 0.5

    def test_run_ayarla_str(self):
        from reymen.sistem.config_manager import run
        sonuc = run("ayarla", "model", "test-model-xyz")
        assert "✅" in sonuc
        assert self.cfg.get("model") == "test-model-xyz"

    def test_run_ayarla_key_yok(self):
        from reymen.sistem.config_manager import run
        sonuc = run("ayarla", "", "val")
        assert "Hata" in sonuc

    def test_run_reset(self):
        from reymen.sistem.config_manager import run
        self.cfg.set("model", "changed")
        sonuc = run("reset")
        assert "✅" in sonuc
        assert self.cfg.get("model") == "mimo-v2.5-pro"

    def test_run_bilinmeyen(self):
        from reymen.sistem.config_manager import run
        sonuc = run("invalid_op")
        assert "Hata" in sonuc


class TestGetConfigSingleton:
    """get_config() singleton davranışı."""

    def setup_method(self):
        import reymen.sistem.config_manager as cm
        cm._cfg = None

    def teardown_method(self):
        import reymen.sistem.config_manager as cm
        cm._cfg = None

    def test_singleton(self):
        from reymen.sistem.config_manager import get_config
        cfg1 = get_config()
        cfg2 = get_config()
        assert cfg1 is cfg2


class TestEnvMapping:
    """Ortam değişkeni映射leri."""

    def setup_method(self):
        from reymen.sistem.config_manager import Config
        self.cfg_path, self._dir = _tmp_config()

    def teardown_method(self):
        if os.path.exists(self.cfg_path):
            os.remove(self.cfg_path)
        os.rmdir(self._dir)

    def test_env_map_tanimli(self):
        from reymen.sistem.config_manager import Config
        assert "REYMEN_MODEL" in Config.ENV_MAP
        assert "DEEPSEEK_API_KEY" in Config.ENV_MAP
        assert "TELEGRAM_BOT_TOKEN" in Config.ENV_MAP

    def test_env_yukleme(self):
        from reymen.sistem.config_manager import Config
        with patch.dict(os.environ, {"REYMEN_MODEL": "env-model"}):
            cfg = Config(config_path=self.cfg_path)
            assert cfg.get("model") == "env-model"
