# -*- coding: utf-8 -*-
# SHIM + standalone — tools/delegate_task_tool.py yönlendirir, _MAIN_PY patch'lenebilir
import sys
from pathlib import Path

from tools.delegate_task_tool import *  # noqa: F401, F403

_MAIN_PY = Path(__file__).parent / "main.py"


def run(gorev: str = "", timeout: int = 60) -> str:
    """Shim wrapper — uses module-level _MAIN_PY (patchable)."""
    if not gorev or not gorev.strip():
        return "[Hata]: gorev parametresi bos olamaz."
    if not _MAIN_PY.exists():
        return f"[Hata]: main.py bulunamadi — {_MAIN_PY}"
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(_MAIN_PY), "--gorev", gorev],
            capture_output=True, text=True, timeout=timeout,
        )
        out = result.stdout.strip()
        return out if out else f"[Tamam] Gorev tamamlandi (cikti yok)"
    except subprocess.TimeoutExpired:
        return "[Hata]: Zaman asimi."
    except Exception as e:
        return f"[Hata]: {e}"
