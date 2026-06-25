# -*- coding: utf-8 -*-
"""
config_manager.py — Merkezi yapılandırma yönetimi.

Tüm ReYMeN yapılandırması tek bir yerden yönetilir.
Öncelik: env > config.yaml > varsayılan

Kullanım:
    from reymen.sistem.config_manager import Config
    cfg = Config()
    cfg.get("model")                    # Varsayılan model
    cfg.get("provider")                 # Varsayılan provider
    cfg.set("model", "mimo-v2.5-pro")   # Değiştir
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Dict


class Config:
    """Merkezi yapılandırma yöneticisi."""

    # Varsayılan yapılandırma
    VARSAYILAN = {
        # Model
        "model": "mimo-v2.5-pro",
        "provider": "xiaomi",
        "temperature": 0.7,
        "max_tokens": 4096,
        "timeout": 120,

        # Motor
        "max_iterations": 90,
        "max_retries": 3,
        "circuit_breaker_threshold": 3,
        "circuit_breaker_permanent": True,

        # Hafıza
        "memory_max_chars": 2200,
        "user_max_chars": 1375,
        "decisions_max_chars": 50000,
        "memory_auto_save": True,

        # Logging
        "log_level": "INFO",
        "log_file": True,
        "log_console": True,
        "log_max_bytes": 10485760,  # 10MB
        "log_backup_count": 5,

        # Güvenlik
        "security_strict": True,
        "allowed_commands": [],
        "blocked_commands": [],

        # Web
        "web_search_provider": "duckduckgo",
        "web_extract_timeout": 30,
        "web_extract_max_urls": 5,

        # Görsel
        "image_generate_provider": "auto",  # auto/fal/openai/huggingface
        "image_save_local": True,

        # Tarayıcı
        "browser_headless": True,
        "browser_type": "chromium",
        "browser_timeout": 30000,

        # Platform
        "telegram_enabled": True,
        "discord_enabled": False,
        "slack_enabled": False,

        # Cron
        "cron_enabled": True,
        "cron_check_interval": 30,  # saniye

        # Performans
        "lazy_loading": True,
        "cache_enabled": True,
        "cache_ttl": 3600,  # saniye

        # Dosya
        "max_file_read_lines": 2000,
        "max_search_results": 50,
        "max_patch_attempts": 9,
    }

    # Ortam değişkeni eşlemeleri (env → config_key)
    ENV_MAP = {
        "XIAOMI_API_KEY": "api_keys.xiaomi",
        "DEEPSEEK_API_KEY": "api_keys.deepseek",
        "OPENAI_API_KEY": "api_keys.openai",
        "FAL_KEY": "api_keys.fal",
        "FAL_API_KEY": "api_keys.fal",
        "HF_TOKEN": "api_keys.huggingface",
        "HUGGINGFACE_TOKEN": "api_keys.huggingface",
        "BRAVE_API_KEY": "api_keys.brave",
        "TELEGRAM_BOT_TOKEN": "telegram.bot_token",
        "TELEGRAM_CHAT_ID": "telegram.chat_id",
        "REYMEN_LOG_LEVEL": "log_level",
        "REYMEN_MODEL": "model",
        "REYMEN_PROVIDER": "provider",
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: Yapılandırma dosyası yolu (None = varsayılan)
        """
        self._path = Path(config_path) if config_path else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "config.json"
        )
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = {}
        self._yukle()

    def _yukle(self):
        """Yapılandırmayı yükler."""
        # 1. Varsayılanları yükle
        self._data = dict(self.VARSAYILAN)

        # 2. Dosyadan yükle (varsa)
        if self._path.exists():
            try:
                dosya_data = json.loads(self._path.read_text(encoding="utf-8"))
                self._derin_birlestir(self._data, dosya_data)
            except Exception:
                pass  # Bozuk dosya → varsayılan kullan

        # 3. Ortam değişkenlerini yükle (en yüksek öncelik)
        self._env_yukle()

    def _derin_birlestir(self, hedef: dict, kaynak: dict):
        """İki sözlüğü derin birleştirir."""
        for k, v in kaynak.items():
            if k in hedef and isinstance(hedef[k], dict) and isinstance(v, dict):
                self._derin_birlestir(hedef[k], v)
            else:
                hedef[k] = v

    def _env_yukle(self):
        """Ortam değişkenlerini yükler."""
        for env_key, config_key in self.ENV_MAP.items():
            deger = os.getenv(env_key)
            if deger is not None:
                self._set_nested(config_key, deger)

    def _set_nested(self, key: str, value: Any):
        """Noktalı anahtar ile iç içe sözlüğe değer atar."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def _get_nested(self, key: str, default: Any = None) -> Any:
        """Noktalı anahtar ile iç içe sözlükten değer okur."""
        keys = key.split(".")
        d = self._data
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    # ── Public API ───────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Yapılandırma değerini okur."""
        return self._get_nested(key, default)

    def set(self, key: str, value: Any) -> None:
        """Yapılandırma değerini ayarlar."""
        self._set_nested(key, value)
        self._kaydet()

    def _kaydet(self):
        """Yapılandırmayı dosyaya kaydeder."""
        try:
            self._path.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8"
            )
        except Exception:
            pass

    def tum(self) -> Dict[str, Any]:
        """Tüm yapılandırmayı döner."""
        return dict(self._data)

    def reset(self) -> None:
        """Varsayılana sıfırlar."""
        self._data = dict(self.VARSAYILAN)
        self._env_yukle()
        self._kaydet()

    def formatla(self) -> str:
        """Yapılandırmayı okunabilir format döner."""
        satirlar = ["📋 Yapılandırma:\n"]
        for k, v in sorted(self._data.items()):
            if isinstance(v, dict):
                satirlar.append(f"\n📁 {k}:")
                for k2, v2 in v.items():
                    satirlar.append(f"  {k2}: {v2}")
            else:
                satirlar.append(f"  {k}: {v}")
        return "\n".join(satirlar)


# ── Global Instance ──────────────────────────────────────────────────────────

_cfg = None

def get_config() -> Config:
    """Global yapılandırma instance'ı döner."""
    global _cfg
    if _cfg is None:
        _cfg = Config()
    return _cfg


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(islem: str = "oku", key: str = "", value: str = "") -> str:
    """Motor entegrasyonu."""
    cfg = get_config()

    if islem == "oku":
        if not key:
            return cfg.formatla()
        deger = cfg.get(key)
        return f"{key}: {deger}" if deger is not None else f"[Hata]: Anahtar bulunamadı: {key}"

    elif islem == "ayarla":
        if not key:
            return "[Hata]: key gerekli."
        # Tip dönüşümü
        if value.lower() in ("true", "false"):
            cfg.set(key, value.lower() == "true")
        elif value.isdigit():
            cfg.set(key, int(value))
        else:
            try:
                cfg.set(key, float(value))
            except ValueError:
                cfg.set(key, value)
        return f"✅ {key} = {value}"

    elif islem == "reset":
        cfg.reset()
        return "✅ Yapılandırma sıfırlandı."

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    cfg = get_config()
    print(cfg.formatla())
