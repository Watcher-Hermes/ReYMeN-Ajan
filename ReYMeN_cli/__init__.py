# -*- coding: utf-8 -*-
"""ReYMeN_cli/__init__.py â€” CLI Modul Kayit Defteri.

Tum CLI modullerini iceri aktarir ve merkezi komut kaydini saglar.
Opsiyonel moduller try/except ile yuklenir; yuklenemezse uyari verilir.
"""

import logging
from typing import Callable

__version__ = "1.0.0"
__release_date__ = "2026-06-16"

logger = logging.getLogger(__name__)

_MODULLER = [
    # Temel CLI modulleri
    "agent", "backup", "browser", "config", "cron", "doctor", "docs",
    "gateway", "memory", "plugin", "security", "session", "skill_import",
    "system", "test",
    # System CLI
    "auth", "build_info", "callbacks", "checkpoints", "clipboard", "colors",
    "debug", "dump", "hooks", "logs",
    # Tool CLI
    "inventory", "mcp_picker", "mcp_security", "mcp_startup", "middleware",
    "pairing", "platforms", "plugins_cmd", "secrets_cli", "tools_config",
    # Service CLI
    "service_manager", "session_listing", "setup", "status", "timeouts",
    "tips", "uninstall", "voice", "web_server", "webhook",
    # Extended CLI
    "active_sessions", "banner", "bundles", "callbacks_cli", "container_boot",
    "copilot_auth", "curator_cli", "dashboard_register", "dep_ensure",
    "env_loader", "fallback_config", "goals", "hooks_cli", "kanban_decompose",
    "kanban_diagnostics", "kanban_specify", "managed_uv", "migrate",
    "model_catalog", "model_cost_guard", "model_normalize", "model_switch",
    "partial_compress", "prompt_size", "runtime_provider", "secret_prompt",
    "send_cmd", "skin_engine", "suggestions_cmd", "win_pty_bridge",
    # BIZ Custom CLI
    "auto_setup", "benchmarks", "broadcast", "cache", "compliance",
    "components", "demo", "diagnostics", "encryption", "feedback", "firewall",
    "localization", "maintenance", "metrics", "monitor", "notifications",
    "optimizer", "package", "permissions", "proxy", "quarantine", "recovery",
    "registry_cli", "reporting", "resources", "rollback", "routing",
    "sandbox", "scheduler", "scoring", "search_cli", "storage", "sync_cli",
    "telemetry", "template", "tracing", "troubleshooting", "update_cli",
    "validation", "watchdog",
    # Gap Tamamlama
    "_parser", "_subprocess_compat", "cli_output", "session_recap",
    "fallback_cmd", "kanban_db", "kanban_swarm", "skills_hub",
    "blueprint_cmd", "memory_setup", "oneshot", "plugins",
    "security_advisories", "write_approval_commands", "stdio",
]

_yuklenen = []
_yuklenemeyen = []

for _modul_adi in _MODULLER:
    try:
        import importlib
        importlib.import_module(f"ReYMeN_cli.{_modul_adi}")
        _yuklenen.append(_modul_adi)
    except Exception as _e:
        _yuklenemeyen.append((_modul_adi, str(_e)))
        logger.debug("ReYMeN_cli.%s yuklenemedi: %s", _modul_adi, _e)

if _yuklenemeyen:
    logger.debug("ReYMeN_cli: %d modul yuklenemedi (graceful degrade)", len(_yuklenemeyen))

_komutlar: dict[str, tuple[str, Callable, str]] = {}


def kaydet(ad: str, kategori: str, fonk: Callable, yardim: str):
    _komutlar[ad] = (kategori, fonk, yardim)


def komut_al(ad: str) -> Callable | None:
    if ad in _komutlar:
        return _komutlar[ad][1]
    return None


def komut_listele(kategori: str = "") -> list[tuple[str, str, str]]:
    sonuc = []
    for ad, (kat, _, yardim) in sorted(_komutlar.items()):
        if not kategori or kat == kategori:
            sonuc.append((ad, kat, yardim))
    return sonuc


def kategorileri_listele() -> list[str]:
    kategoriler = set()
    for _, (kat, _, _) in _komutlar.items():
        kategoriler.add(kat)
    return sorted(kategoriler)


def yuklenme_durumu() -> dict:
    return {"yuklenen": len(_yuklenen), "yuklenemeyen": len(_yuklenemeyen),
            "hatalar": _yuklenemeyen}

