# -*- coding: utf-8 -*-
"""
test_config_loader.py — config_loader.py için birim testler.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from reymen.sistem.config_loader import (
    load_yaml_safe,
    _env_or,
    _resolve_provider_api_key,
    load_config,
    merge_with_existing,
)


# ── _env_or ─────────────────────────────────────────────────────────────────

class TestEnvOr:
    def test_env_var_set(self):
        with patch.dict(os.environ, {"TEST_ENV_VAR": "hello"}):
            assert _env_or("default", "TEST_ENV_VAR") == "hello"

    def test_env_var_empty(self):
        with patch.dict(os.environ, {"TEST_ENV_VAR": "  "}):
            assert _env_or("default", "TEST_ENV_VAR") == "default"

    def test_env_var_masked(self):
        """*** ile başlayan maskeli key fallback'e gider."""
        with patch.dict(os.environ, {"TEST_ENV_VAR": "***"}):
            assert _env_or("default", "TEST_ENV_VAR") == "default"

    def test_env_var_not_set(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_ENV_VAR_NONEXIST", None)
            assert _env_or("default", "TEST_ENV_VAR_NONEXIST") == "default"

    def test_value_none_uses_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_ENV_VAR_NONEXIST", None)
            assert _env_or(None, "TEST_ENV_VAR_NONEXIST", "fallback") == "fallback"

    def test_value_priority_over_default(self):
        """value varsa ve env yoksa value döner."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_ENV_VAR_NONEXIST", None)
            assert _env_or("from_value", "TEST_ENV_VAR_NONEXIST", "fallback") == "from_value"

    def test_env_stripped(self):
        with patch.dict(os.environ, {"TEST_ENV_VAR": "  trimmed  "}):
            assert _env_or("default", "TEST_ENV_VAR") == "trimmed"


# ── load_yaml_safe ──────────────────────────────────────────────────────────

class TestLoadYamlSafe:
    def test_missing_file(self):
        result = load_yaml_safe(Path("/nonexistent/config.yaml"))
        assert result is None

    def test_valid_yaml(self, tmp_path):
        p = tmp_path / "test.yaml"
        p.write_text("key: value\nlist:\n  - a\n  - b\n", encoding="utf-8")
        result = load_yaml_safe(p)
        assert result == {"key": "value", "list": ["a", "b"]}

    def test_empty_yaml(self, tmp_path):
        p = tmp_path / "empty.yaml"
        p.write_text("", encoding="utf-8")
        result = load_yaml_safe(p)
        # safe_load returns None for empty → non-dict → None
        assert result is None

    def test_non_dict_yaml(self, tmp_path):
        p = tmp_path / "list.yaml"
        p.write_text("- item1\n- item2\n", encoding="utf-8")
        result = load_yaml_safe(p)
        assert result is None

    def test_invalid_yaml_syntax(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("key: value\n  bad indent:\n - wrong", encoding="utf-8")
        # May or may not raise — depends on content. Just ensure no crash.
        result = load_yaml_safe(p)
        # Could be None (on error) or dict (if yaml tolerates it)
        assert result is None or isinstance(result, dict)


# ── _resolve_provider_api_key ──────────────────────────────────────────────

class TestResolveProviderApiKey:
    def test_no_env_key(self):
        cfg = {"base_url": "http://localhost:1234", "api_key": "sk-test"}
        result = _resolve_provider_api_key(cfg)
        assert result["api_key"] == "sk-test"
        assert "api_key_env" not in result

    def test_with_env_key(self):
        with patch.dict(os.environ, {"MY_PROVIDER_KEY": "resolved-key"}):
            cfg = {"base_url": "http://localhost", "api_key_env": "MY_PROVIDER_KEY"}
            result = _resolve_provider_api_key(cfg)
            assert result["api_key"] == "resolved-key"
            assert "api_key_env" not in result

    def test_env_key_not_set(self):
        os.environ.pop("MISSING_PROVIDER_KEY", None)
        cfg = {"base_url": "http://localhost", "api_key_env": "MISSING_PROVIDER_KEY"}
        result = _resolve_provider_api_key(cfg)
        assert result["api_key"] == ""


# ── load_config ─────────────────────────────────────────────────────────────

class TestLoadConfig:
    def test_no_yaml(self, tmp_path):
        """Yok dosya ver → tüm varsayılanlar dönsün."""
        result = load_config(str(tmp_path / "nonexistent.yaml"))
        assert result["default_model"] is not None
        assert result["max_turns"] == 15
        assert result["memory_char_limit"] == 50000
        assert result["providers"] == {}

    def test_with_yaml(self, tmp_path):
        yaml_content = """
general:
  default_model: my-model
  default_provider: my-provider
  max_turns: 5
  secure_binding: false
  memory_char_limit: 10000
providers:
  myprovider:
    base_url: http://myprovider:1234
    api_key: sk-123
state_machine:
  enabled: false
auto_recovery:
  check_interval_sec: 30
"""
        p = tmp_path / "config.yaml"
        p.write_text(yaml_content, encoding="utf-8")
        result = load_config(str(p))
        assert result["default_model"] == "my-model"
        assert result["default_provider"] == "my-provider"
        assert result["max_turns"] == 5
        assert result["secure_binding"] is False
        assert result["memory_char_limit"] == 10000
        assert "myprovider" in result["providers"]
        assert result["state_machine"]["enabled"] is False
        assert result["auto_recovery"]["check_interval_sec"] == 30

    def test_env_override(self, tmp_path):
        with patch.dict(os.environ, {"REYMEN_DEFAULT_MODEL": "env-model"}):
            result = load_config(str(tmp_path / "nonexistent.yaml"))
            assert result["default_model"] == "env-model"

    def test_max_turns_env_override(self, tmp_path):
        with patch.dict(os.environ, {"REYMEN_MAX_TURNS": "42"}):
            result = load_config(str(tmp_path / "nonexistent.yaml"))
            assert result["max_turns"] == 42


# ── merge_with_existing ────────────────────────────────────────────────────

class TestMergeWithExisting:
    def test_simple_merge(self):
        existing = {"default_model": "old", "providers": {"p1": {"a": 1}}}
        yaml_cfg = {"default_model": "new"}
        merged = merge_with_existing(yaml_cfg, existing)
        assert merged["default_model"] == "new"

    def test_new_provider_added(self):
        existing = {"providers": {"p1": {"base_url": "u1"}}}
        yaml_cfg = {"providers": {"p2": {"base_url": "u2", "api_key": "k2"}}}
        merged = merge_with_existing(yaml_cfg, existing)
        assert "p2" in merged["providers"]
        assert merged["providers"]["p1"]["base_url"] == "u1"

    def test_existing_provider_base_url_override(self):
        existing = {"providers": {"p1": {"base_url": "old"}}}
        yaml_cfg = {"providers": {"p1": {"base_url": "new", "api_key": "k"}}}
        merged = merge_with_existing(yaml_cfg, existing)
        assert merged["providers"]["p1"]["base_url"] == "new"
        assert merged["providers"]["p1"]["api_key"] == "k"

    def test_fallback_none(self):
        existing = {"fallback_model": {"provider": "deepseek"}}
        yaml_cfg = {"fallback_model": None}
        merged = merge_with_existing(yaml_cfg, existing)
        assert "fallback_model" not in merged

    def test_new_keys_copied(self):
        existing = {}
        yaml_cfg = {"state_machine": {"enabled": True}, "logging": {"level": "INFO"}}
        merged = merge_with_existing(yaml_cfg, existing)
        assert merged["state_machine"]["enabled"] is True
        assert merged["logging"]["level"] == "INFO"

    def test_telegram_merge_empty_existing(self):
        existing = {}
        yaml_cfg = {"telegram": {"token": "tok123", "chat_id": "999"}}
        merged = merge_with_existing(yaml_cfg, existing)
        assert merged["telegram"]["token"] == "tok123"


# ── Syntax check ───────────────────────────────────────────────────────────

def test_syntax():
    import ast
    path = Path(__file__).parent.parent / "reymen" / "sistem" / "config_loader.py"
    ast.parse(path.read_text(encoding="utf-8"))
