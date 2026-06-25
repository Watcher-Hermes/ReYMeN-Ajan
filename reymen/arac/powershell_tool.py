# -*- coding: utf-8 -*-
"""
powershell_tool.py — PowerShell komut çalıştırma aracı.

ReYMeN Agent'in PowerShell komutlarını çalıştırmasını sağlar.
CMD, PowerShell ve bash komutlarını destekler.

Kurulum: Gerek yok (Python subprocess)

Kullanım:
    from reymen.arac.powershell_tool import powershell_calistir
    sonuc = powershell_calistir("Get-Process | Select-Object -First 5")
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict


def powershell_calistir(komut: str, calisma_dizini: str = "",
                        timeout: int = 60, yonetici: bool = False) -> Dict:
    """
    PowerShell komutu çalıştırır.

    Args:
        komut: Çalıştırılacak PowerShell komutu
        calisma_dizini: Çalışma dizini (opsiyonel)
        timeout: Zaman aşımı (saniye)
        yonetici: Yönetici modunda çalıştır (elevated)

    Returns:
        {"stdout", "stderr", "exit_code", "error", "sure"}
    """
    if not komut or not komut.strip():
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": "Komut boş olamaz.", "sure": 0}

    baslama = time.time()

    try:
        # PowerShell komutu oluştur
        if yonetici:
            # Yönetici modunda çalıştır
            ps_komut = (
                f'Start-Process powershell -Verb RunAs -ArgumentList '
                f'"-NoProfile -ExecutionPolicy Bypass -Command {komut}" -Wait'
            )
        else:
            ps_komut = komut

        # subprocess ile çalıştır
        # PowerShell encoding ayarı (Türkçe karakter desteği)
        encoded_cmd = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {ps_komut}"

        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", encoded_cmd],
            capture_output=True,
            timeout=timeout,
            cwd=calisma_dizini if calisma_dizini else None,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        # Encoding handling
        stdout = result.stdout.decode("utf-8", errors="replace").strip() if result.stdout else ""
        stderr = result.stderr.decode("utf-8", errors="replace").strip() if result.stderr else ""

        sure = time.time() - baslama

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": result.returncode,
            "error": None,
            "sure": round(sure, 2),
        }

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": f"Zaman aşımı ({timeout}s)", "sure": timeout}
    except FileNotFoundError:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": "PowerShell bulunamadı.", "sure": 0}
    except Exception as e:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": str(e), "sure": 0}


def cmd_calistir(komut: str, calisma_dizini: str = "",
                 timeout: int = 60) -> Dict:
    """
    CMD komutu çalıştırır.

    Args:
        komut: Çalıştırılacak CMD komutu
        calisma_dizini: Çalışma dizini
        timeout: Zaman aşımı (saniye)

    Returns:
        {"stdout", "stderr", "exit_code", "error", "sure"}
    """
    if not komut or not komut.strip():
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": "Komut boş olamaz.", "sure": 0}

    baslama = time.time()

    try:
        result = subprocess.run(
            ["cmd", "/c", komut],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=calisma_dizini if calisma_dizini else None,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        sure = time.time() - baslama

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "error": None,
            "sure": round(sure, 2),
        }

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": f"Zaman aşımı ({timeout}s)", "sure": timeout}
    except Exception as e:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": str(e), "sure": 0}


def bash_calistir(komut: str, calisma_dizini: str = "",
                  timeout: int = 60) -> Dict:
    """
    Bash komutu çalıştırır (Git Bash / MSYS).

    Args:
        komut: Çalıştırılacak bash komutu
        calisma_dizini: Çalışma dizini
        timeout: Zaman aşımı (saniye)

    Returns:
        {"stdout", "stderr", "exit_code", "error", "sure"}
    """
    if not komut or not komut.strip():
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": "Komut boş olamaz.", "sure": 0}

    baslama = time.time()

    # Git Bash yolu
    bash_yollari = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"C:\Git\bin\bash.exe",
    ]

    bash_yolu = None
    for yol in bash_yollari:
        if Path(yol).exists():
            bash_yolu = yol
            break

    if not bash_yolu:
        # PATH'te bash ara
        try:
            result = subprocess.run(["where", "bash"], capture_output=True, text=True)
            if result.returncode == 0:
                bash_yolu = result.stdout.strip().split("\n")[0]
        except Exception:
            pass

    if not bash_yolu:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": "Bash bulunamadı. Git Bash kurun.", "sure": 0}

    try:
        result = subprocess.run(
            [bash_yolu, "-c", komut],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=calisma_dizini if calisma_dizini else None,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        sure = time.time() - baslama

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "error": None,
            "sure": round(sure, 2),
        }

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": f"Zaman aşımı ({timeout}s)", "sure": timeout}
    except Exception as e:
        return {"stdout": "", "stderr": "", "exit_code": -1,
                "error": str(e), "sure": 0}


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(komut: str = "", shell: str = "powershell", calisma_dizini: str = "",
        timeout: int = 60, yonetici: bool = False) -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    Args:
        komut: Çalıştırılacak komut
        shell: powershell/cmd/bash
        calisma_dizini: Çalışma dizini
        timeout: Zaman aşımı (saniye)
        yonetici: Yönetici modu (sadece powershell)

    Returns:
        Formatlı çıktı
    """
    if not komut or not komut.strip():
        return "[Hata]: komut parametresi boş olamaz."

    if shell == "powershell":
        sonuc = powershell_calistir(komut, calisma_dizini, timeout, yonetici)
    elif shell == "cmd":
        sonuc = cmd_calistir(komut, calisma_dizini, timeout)
    elif shell == "bash":
        sonuc = bash_calistir(komut, calisma_dizini, timeout)
    else:
        return f"[Hata]: Bilinmeyen shell: {shell}. powershell/cmd/bash kullanın."

    if sonuc.get("error"):
        return f"[Hata]: {sonuc['error']}"

    cikti = ""
    if sonuc["stdout"]:
        cikti += sonuc["stdout"]
    if sonuc["stderr"]:
        cikti += f"\n[HATA]: {sonuc['stderr']}"

    cikti += f"\n\n[Çıkış kodu: {sonuc['exit_code']} | Süre: {sonuc['sure']}s]"

    return cikti if cikti.strip() else f"[Tamam] Komut çalıştırıldı (çıktı yok). [Çıkış kodu: {sonuc['exit_code']}]"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python powershell_tool.py <komut> [shell]")
        print("Shell: powershell (varsayılan), cmd, bash")
        sys.exit(1)

    komut = " ".join(sys.argv[1:])
    shell = "powershell"
    for s in ["powershell", "cmd", "bash"]:
        if f"--shell={s}" in komut:
            shell = s
            komut = komut.replace(f"--shell={s}", "").strip()
            break

    print(run(komut=komut, shell=shell))
