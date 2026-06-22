# -*- coding: utf-8 -*-
"""ReYMeN_cli/_subprocess_compat.py — Platformlararasi Alt Surec Yardimcilari.

Windows ve Linux/Mac uyumlu subprocess islemleri icin yardimci fonksiyonlar.
CREATE_NO_WINDOW, zaman-asimi, sessiz calistirma gibi ozellikler sunar.
"""

import os
import signal
import subprocess
import sys
from typing import Optional


def pencere_komutu(komut: list) -> list:
    """Windows'ta CREATE_NO_WINDOW flag'i ekleyerek komutu calistir.

    Windows'ta konsol penceresi acilmasini engeller.
    Linux/Mac'te komut oldugu gibi doner.

    Args:
        komut: Calistirilacak komut listesi (ornek: ['python', 'script.py']).

    Returns:
        list: CREATE_NO_WINDOW flag'i ile zenginlestirilmis komut (Windows),
              veya orijinal komut (Linux/Mac).
    """
    try:
        if sys.platform == "win32":
            import subprocess as sp_mod
            CREATE_NO_WINDOW = 0x08000000
            if hasattr(sp_mod, "CREATE_NO_WINDOW"):
                CREATE_NO_WINDOW = sp_mod.CREATE_NO_WINDOW
            return komut + [CREATE_NO_WINDOW]
        return komut
    except Exception:
        return komut


def windows_hide_flags() -> int:
    """Windows'ta konsol penceresi acmayan CREATE_NO_WINDOW flag degerini dondur.

    Returns:
        int: Windows'ta CREATE_NO_WINDOW sabiti, diger platformlarda 0.
    """
    if sys.platform == "win32":
        try:
            return subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        except AttributeError:
            return 0x08000000  # CREATE_NO_WINDOW
    return 0


def bekle_sureli(proc: subprocess.Popen, timeout: int = 30) -> bool:
    """Alt sureci belirtilen sure boyunca bekle, zaman-asiminda sonlandir.

    Args:
        proc: Beklenecek subprocess.Popen nesnesi.
        timeout: Bekleme suresi (saniye, varsayilan: 30).

    Returns:
        bool: Surec basariyla tamamlandiysa True,
              zaman-asimi veya hata durumunda False.
    """
    try:
        proc.wait(timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        try:
            if sys.platform == "win32":
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            else:
                os.kill(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.kill(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=2)
        except Exception:
            pass
        return False
    except Exception:
        return False


def sessiz_calistir(komut: list, timeout: int = 30) -> tuple:
    """Komutu sessizce calistir ve (cikis_kodu, cikti) dondur.

    stdout ve stderr yakalanir, konsola yazdirilmaz.
    Windows'ta CREATE_NO_WINDOW flag'i otomatik eklenir.

    Args:
        komut: Calistirilacak komut listesi.
        timeout: Maksimum bekleme suresi (saniye, varsayilan: 30).

    Returns:
        tuple[int, str]: (cikis_kodu, stdout+stderr ciktisi).
                         Zaman-asiminda cikis_kodu -1 olur.
    """
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        proc = subprocess.Popen(
            komut,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        try:
            stdout_bytes, _ = proc.communicate(timeout=timeout)
            cikis_kodu = proc.returncode
            cikti = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            return (cikis_kodu, cikti)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_bytes, _ = proc.communicate(timeout=5)
            cikti = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
            return (-1, cikti + "\n[TIMEOUT] Surec zaman-asimina ugradi.")
    except FileNotFoundError:
        return (-2, f"[HATA] Komut bulunamadi: {komut[0] if komut else '?'}")
    except PermissionError:
        return (-3, f"[HATA] Komut calistirma izni yok: {komut[0] if komut else '?'}")
    except Exception as e:
        return (-99, f"[HATA] Beklenmeyen subprocess hatasi: {e}")
