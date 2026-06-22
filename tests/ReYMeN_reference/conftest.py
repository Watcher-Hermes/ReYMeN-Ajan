# -*- coding: utf-8 -*-
"""tests/ReYMeN_reference/conftest.py — ReYMeN referans testleri ön hazırlık.

tests/ReYMeN_reference/cron/__init__.py oldugundan pytest, tests/ReYMeN_reference/
dizinini sys.path'a ekler ve proje koku cron/ paketini golgeleyebilir.

Bu conftest:
  - pytest_collect_file: her test dosyasi import edilmeden once cron golgesini gider
  - pytest_runtest_setup: her test oncesi cron golgesini gider (fixture-time importlar)
"""
import importlib.util
import sys
from pathlib import Path

# Proje koku: tests/ReYMeN_reference/conftest.py -> parent x3
_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
_CRON_INIT = _PROJECT_ROOT / "cron" / "__init__.py"

# Proje kokunu sys.path'a ekle (modül yüklenince hemen).
_proj_str = str(_PROJECT_ROOT)
if _proj_str not in sys.path:
    sys.path.insert(0, _proj_str)


def _ensure_real_cron() -> None:
    """Proje koku cron/ paketinin sys.modules'ta dogru sekilde yuklu olmasini sagla."""
    # Proje kokunu sys.path basina koy.
    if _proj_str in sys.path:
        sys.path.remove(_proj_str)
    sys.path.insert(0, _proj_str)

    # Mevcut cron modulu dogru mu?
    cron_mod = sys.modules.get("cron")
    if cron_mod is not None:
        current = Path(getattr(cron_mod, "__file__", "") or "").resolve()
        if current == _CRON_INIT:
            return  # Zaten dogru

        # Yanlis cron: cron.conftest'i koru, digerlerini temizle.
        stale = [
            k for k in list(sys.modules)
            if (k == "cron" or k.startswith("cron."))
            and not k.endswith(".conftest")
            and "conftest" not in k
        ]
        for key in stale:
            del sys.modules[key]

    # Proje koku cron paketini yuklhe.
    spec = importlib.util.spec_from_file_location(
        "cron",
        str(_CRON_INIT),
        submodule_search_locations=[str(_CRON_INIT.parent)],
    )
    cron_pkg = importlib.util.module_from_spec(spec)
    sys.modules["cron"] = cron_pkg
    spec.loader.exec_module(cron_pkg)


def pytest_collect_file(parent, file_path):
    """Her test dosyasi kolleksiyonundan once cron golgesini gider."""
    _ensure_real_cron()


def pytest_runtest_setup(item):
    """Her test kurulumundan once cron golgesini gider."""
    _ensure_real_cron()
