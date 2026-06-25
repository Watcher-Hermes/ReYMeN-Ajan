# -*- coding: utf-8 -*-
"""
desktop/python_bridge.py — Python <-> Electron IPC Bridge.

Electron main process'i ile web_ui.py arasinda kopru gorevi gorur.
JSON tabanli stdin/stdout iletisimi.

Kullanim (Electron tarafindan cagrilir):
    python python_bridge.py --port 8765
"""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path


# ── Sabitler ────────────────────────────────────────────────────────────
WEB_UI_PORT = int(os.environ.get("WEB_UI_PORT", "8765"))
PROJE_KOK = Path(__file__).parent.parent
WEB_UI_PATH = PROJE_KOK / "web_ui.py"

# asar/extraResources fallback: web_ui.py resources'ta da olabilir
_EXTRA_RESOURCES = Path(os.environ.get("RESOURCES_PATH", ""))
if not WEB_UI_PATH.exists() and _EXTRA_RESOURCES.exists():
    WEB_UI_PATH = _EXTRA_RESOURCES / "web_ui.py"
# asar.unpacked fallback
if not WEB_UI_PATH.exists():
    _ASAR_UNPACKED = Path(__file__).parent.parent.parent / "app.asar.unpacked"
    if _ASAR_UNPACKED.exists():
        WEB_UI_PATH = _ASAR_UNPACKED / "desktop" / "python_bridge.py"
        PROJE_KOK = WEB_UI_PATH.parent.parent


def web_ui_baslat() -> subprocess.Popen | None:
    """
    web_ui.py'yi headless modda arkaplanda baslat.
    
    Returns:
        subprocess.Popen: Baslatilan process, veya None (hata).
    """
    if not WEB_UI_PATH.exists():
        print(json.dumps({
            "tur": "hata",
            "mesaj": f"web_ui.py bulunamadi: {WEB_UI_PATH}",
        }))
        return None

    print(json.dumps({
        "tur": "bilgi",
        "mesaj": f"web_ui baslatiliyor: {WEB_UI_PATH}",
    }))

    try:
        env = os.environ.copy()
        env.update({"REYMEN_DESKTOP": "1", "PYTHONUNBUFFERED": "1", "WEB_UI_PORT": str(WEB_UI_PORT)})
        proc = subprocess.Popen(
            [sys.executable, str(WEB_UI_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        return proc
    except FileNotFoundError:
        print(json.dumps({
            "tur": "hata",
            "mesaj": f"Python yorumlayicisi bulunamadi: {sys.executable}",
        }))
        return None
    except Exception as e:
        print(json.dumps({
            "tur": "hata",
            "mesaj": f"web_ui baslatilamadi: {e}",
        }))
        return None


def web_ui_durum_kontrol(proc: subprocess.Popen) -> bool:
    """
    web_ui process'inin calisip calismadigini kontrol et.
    
    Args:
        proc: subprocess.Popen nesnesi.
    
    Returns:
        bool: True calisiyor, False degil.
    """
    if proc is None:
        return False
    poll = proc.poll()
    return poll is None  # None = hala calisiyor


def web_ui_durdur(proc: subprocess.Popen):
    """
    web_ui process'ini guvenli sekilde durdur.
    
    Once SIGTERM gonder, 3 sn icinde kapanmazsa SIGKILL.
    
    Args:
        proc: subprocess.Popen nesnesi.
    """
    if proc is None:
        return
    
    proc.terminate()  # SIGTERM
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()  # SIGKILL
        proc.wait()

    print(json.dumps({
        "tur": "bilgi",
        "mesaj": "web_ui durduruldu",
    }))


def komut_gonder(komut: str, args: dict = None) -> dict:
    """
    Electron'dan gelen komutu web_ui API'sine ilet.
    
    Args:
        komut: Komut adi (ornek: "status", "restart").
        args: Komut parametreleri (opsiyonel).
    
    Returns:
        dict: API yaniti.
    
    Ornek:
        >>> komut_gonder("status")
        {"backend": "calisiyor", "uptime": "120s"}
    """
    try:
        import requests
        
        url = f"http://localhost:{WEB_UI_PORT}/api/komut"
        resp = requests.post(
            url,
            json={"komut": komut, "args": args or {}},
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        return resp.json()
    
    except ImportError:
        return {"hata": "requests kutuphanesi kurulu degil"}
    except requests.exceptions.ConnectionError:
        return {"hata": f"Web UI calismiyor (port {WEB_UI_PORT})"}
    except requests.exceptions.Timeout:
        return {"hata": "Web UI yanit vermedi (timeout 10s)"}
    except Exception as e:
        return {"hata": str(e)}


if __name__ == "__main__":
    proc = web_ui_baslat()
    if proc:
        print(json.dumps({"tur": "hazir", "port": WEB_UI_PORT}))
        # Electron tarafından yönetilen process — arkaplanda kal
        import signal
        signal.signal(signal.SIGTERM, lambda *_: web_ui_durdur(proc))
        try:
            proc.wait()
        except (KeyboardInterrupt, EOFError):
            web_ui_durdur(proc)
