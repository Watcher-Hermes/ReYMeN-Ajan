# -*- coding: utf-8 -*-
"""
reymen_logging.py — Merkezi logging modülü.

Tüm ReYMeN modülleri bu modülü kullanır.
print() yerine logger kullanır.

Kullanım:
    from reymen.sistem.reymen_logging import get_logger
    logger = get_logger(__name__)
    logger.info("Başlatılıyor")
    logger.warning("Uyarı")
    logger.error("Hata")
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


# ── Log Formatı ──────────────────────────────────────────────────────────────

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log dizini
LOG_DIR = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Varsayılan log dosyası
LOG_FILE = LOG_DIR / "reymen.log"

# Global logger registry (duplicate handler önleme)
_initialized = False
_loggers = {}


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None,
                  console: bool = True, max_bytes: int = 10 * 1024 * 1024,
                  backup_count: int = 5) -> None:
    """
    Logging sistemini başlatır.

    Args:
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log dosyası yolu (None = varsayılan)
        console: Konsola yazsın mı?
        max_bytes: Max log dosyası boyutu (byte)
        backup_count: Eski log dosyası sayısı
    """
    global _initialized
    if _initialized:
        return

    root_logger = logging.getLogger("reymen")
    root_logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler (RotatingFileHandler)
    try:
        from logging.handlers import RotatingFileHandler
        file_path = Path(log_file) if log_file else LOG_FILE
        file_handler = RotatingFileHandler(
            str(file_path), maxBytes=max_bytes, backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception:
        pass  # Log dosyası yazılamazsa konsola devam et

    _initialized = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Modül için logger döner.

    Args:
        name: Logger adı (genellikle __name__)
        level: Özel log seviyesi (None = varsayılan)

    Returns:
        logging.Logger instance
    """
    if not _initialized:
        setup_logging()

    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(f"reymen.{name}")
    if level is not None:
        logger.setLevel(level)

    _loggers[name] = logger
    return logger


def get_log_level(level_str: str) -> int:
    """Log seviyesi string'ini int'e çevirir."""
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return levels.get(level_str.lower(), logging.INFO)


# ── Modül Başlatma ───────────────────────────────────────────────────────────

# Ortam değişkeninden log seviyesi
_env_level = os.getenv("REYMEN_LOG_LEVEL", "INFO").upper()
_default_level = getattr(logging, _env_level, logging.INFO)

# Otomatik başlatma (import edildiğinde)
setup_logging(level=_default_level)
