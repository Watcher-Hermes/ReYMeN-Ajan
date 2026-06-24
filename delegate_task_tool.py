# -*- coding: utf-8 -*-
"""SHIM — delegate_task_tool — test monkeypatching destekli."""
from __future__ import annotations
import subprocess
import sys
import json
from pathlib import Path

_MAIN_PY = Path(__file__).resolve().parent / "main.py"
_TIMEOUT = 60


def run(
    gorev: str = "",
    zaman_asimi: int = _TIMEOUT,
    json_cikti: bool = False,
) -> str:
    gorev = gorev.strip()
    if not gorev:
        return "[Hata]: gorev parametresi gerekli."

    if not _MAIN_PY.exists():
        return f"[Hata]: main.py bulunamadi — {_MAIN_PY}"

    try:
        zaman_asimi = max(5, min(int(zaman_asimi), 300))
    except (TypeError, ValueError):
        zaman_asimi = _TIMEOUT

    try:
        proc = subprocess.run(
            [sys.executable, str(_MAIN_PY), "--gorev", gorev],
            capture_output=True,
            text=True,
            timeout=zaman_asimi,
        )
    except subprocess.TimeoutExpired:
        return f"[Hata]: Gorev {zaman_asimi}s icinde tamamlanamadi."
    except FileNotFoundError:
        return "[Hata]: Python yorumlayicisi veya main.py bulunamadi."
    except Exception as e:
        return f"[Hata]: Alt process baslatılamadi — {e}"

    if proc.returncode != 0:
        stderr = proc.stderr.strip()[:500] if proc.stderr else "—"
        return f"[Hata]: Process {proc.returncode} koduyla cikti.\nStderr: {stderr}"

    cikti = proc.stdout.strip()
    if not cikti:
        return "[Tamam] Process tamamlandi; cikti yok."

    if json_cikti:
        try:
            veri = json.loads(cikti)
            return json.dumps(veri, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass

    return f"[Sonuc]\n{cikti[:3000]}"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("GOREV_DEVRET", run, "Gorevi alt main.py process'ine devret")
