# -*- coding: utf-8 -*-
"""
conftest.py — ReYMeN testleri icin paylasimli fiksturler.

ReYMeN conftest.py'den uyarlanmistir. ReYMeN yapisina uygun:
  - ReYMeN'e ozel import'lar kaldirildi
  - ReYMeN_HOME yerine temp dizin kullanilir
  - Plugin sistemi yok, TIRITH yok
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest

# Proje kokunu ekle
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Subdir'leri de ekle (shim module'lar agent/ tools/ altindaki modullere yonlenir)
for _sub in ['agent', 'tools', 'plugins', 'plugins/platforms/discord',
             'optional-skills/productivity/memento-flashcards/scripts']:
    _p = str(PROJECT_ROOT / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Unix-only module'lar icin Windows'ta dummy stub'lar
import types as _types
for _unix_mod in ('termios', 'curses', 'pwd'):
    if _unix_mod not in sys.modules:
        try:
            __import__(_unix_mod)
        except ImportError:
            _mod = _types.ModuleType(_unix_mod)
            _mod.__file__ = f'<conftest-{_unix_mod}-stub>'
            sys.modules[_unix_mod] = _mod

# termios sabitlerini ekle (tty.py bunlara ihtiyac duyar)
_termios_mod = sys.modules.get('termios')
if _termios_mod is not None:
    for _const_name, _const_val in [
        ('TCSAFLUSH', 2), ('TCSADRAIN', 1), ('TCSANOW', 0),
        ('ECHO', 8), ('ICANON', 2), ('ISIG', 1),
    ]:
        if not hasattr(_termios_mod, _const_name):
            setattr(_termios_mod, _const_name, _const_val)

# tty modulu de Windows'ta yoksa stub ekle
if 'tty' not in sys.modules:
    try:
        import tty  # noqa: F401
    except (ImportError, NameError, AttributeError):
        _tty_mod = _types.ModuleType('tty')
        _tty_mod.setraw = lambda fd, when=None: None
        _tty_mod.setcbreak = lambda fd, when=None: None
        sys.modules['tty'] = _tty_mod

# pty modulu Windows'ta yoksa stub ekle
if 'pty' not in sys.modules:
    try:
        import pty  # noqa: F401
    except (ImportError, NameError, AttributeError):
        _pty_mod = _types.ModuleType('pty')
        sys.modules['pty'] = _pty_mod

# run_interrupt_test.py pytest test degil, toplamadan cikar
collect_ignore = [str(PROJECT_ROOT / 'tests' / 'run_interrupt_test.py')]


@pytest.fixture(autouse=True)
def _hermetic_environment(tmp_path, monkeypatch):
    """Test ortamini izole et: env var'larini temizle, temp dizin kullan."""

    # 1. Credential env var'larini temizle
    _credential_suffixes = (
        "_API_KEY", "_TOKEN", "_SECRET", "_PASSWORD",
        "_CREDENTIALS", "_ACCESS_KEY", "_SECRET_ACCESS_KEY",
        "_PRIVATE_KEY", "_OAUTH_TOKEN", "_WEBHOOK_SECRET",
        "_ENCRYPT_KEY", "_APP_SECRET", "_CLIENT_SECRET",
        "_AES_KEY",
    )
    _credential_names = frozenset({
        "GITHUB_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "TELEGRAM_BOT_TOKEN", "DISCORD_BOT_TOKEN",
        "REYMEN_OTOMATIK_ONAY",
    })

    for name in list(os.environ.keys()):
        if name in _credential_names or any(name.endswith(s) for s in _credential_suffixes):
            monkeypatch.delenv(name, raising=False)

    # 2. Ortam degiskenlerini sabitle
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.setenv("PYTHONHASHSEED", "0")

    # 3. Temp dizin
    fake_home = tmp_path / "ReYMeN_test"
    fake_home.mkdir()
    (fake_home / "skills").mkdir()
    monkeypatch.setenv("ReYMeN_HOME", str(fake_home))
    monkeypatch.chdir(fake_home)


@pytest.fixture()
def tmp_dir(tmp_path):
    """Gecici klasor (otomatik temizlenir)."""
    return tmp_path


@pytest.fixture()
def mock_config():
    """Basit test config'i."""
    return {
        "model": "test/mock-model",
        "toolsets": ["terminal", "file"],
        "max_turns": 10,
        "compression": {"enabled": False},
    }
