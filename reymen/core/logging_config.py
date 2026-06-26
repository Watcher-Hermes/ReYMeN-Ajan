# -*- coding: utf-8 -*-
"""
reymen.core.logging_config — Merkezi logging yapilandirmasi.

Kullanim:
    from reymen.core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Mesaj")
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Modul icin yapilandirilmis logger dondurur.

    Args:
        name: Modul adi (__name__).

    Returns:
        Yapilandirilmis Logger nesnesi.
    """
    return logging.getLogger(name)


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    json_format: bool = False,
) -> None:
    """Uygulama geneli logging'i yapilandirir.

    Args:
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log dosyasi yolu. None = sadece konsol.
        json_format: True = JSON format (production/ELK icin)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()

    if json_format:
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"module":"%(name)s","line":%(lineno)d,'
            '"message":"%(message)s"}'
        )
    else:
        fmt = (
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(lineno)d | %(message)s"
        )

    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # Konsol handler (her zaman)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Dosya handler (opsiyonel)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Gurtultulu kutuphaneleri sustur
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
