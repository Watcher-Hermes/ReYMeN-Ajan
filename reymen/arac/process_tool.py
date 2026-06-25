# -*- coding: utf-8 -*-
"""
process_tool.py — Background process yönetimi.

Hermes Agent process_tool karşılığı.
Arka plan işlemlerini başlat, izle, durdur, log al.

Dosya: .ReYMeN/processes.json

Kullanım:
    from reymen.arac.process_tool import ProcessManager
    mgr = ProcessManager()
    pid = mgr.baslat("python train.py", calisma_dizini="/workspace")
    print(mgr.durum(pid))
"""

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class ProcessManager:
    """Arka plan process yöneticisi."""

    def __init__(self, log_dir: Optional[str] = None):
        self._dir = Path(log_dir) if log_dir else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "processes"
        )
        self._dir.mkdir(parents=True, exist_ok=True)
        self._procler: Dict[str, Dict] = {}
        self._yukle()

    def _yukle(self):
        """Kayıtlı process bilgilerini yükler."""
        meta = self._dir / "meta.json"
        if meta.exists():
            try:
                self._procler = json.loads(meta.read_text(encoding="utf-8"))
            except Exception:
                self._procler = {}

    def _kaydet(self):
        """Process bilgilerini kaydeder."""
        meta = self._dir / "meta.json"
        meta.write_text(json.dumps(self._procler, indent=2, ensure_ascii=False, default=str),
                        encoding="utf-8")

    def _log_yolu(self, pid: str) -> Path:
        return self._dir / f"{pid}.log"

    def baslat(self, komut: str, calisma_dizini: str = "",
               env: Optional[Dict] = None, timeout: Optional[int] = None) -> str:
        """
        Arka plan process başlatır.

        Args:
            komut: Çalıştırılacak komut
            calisma_dizini: Çalışma dizini
            env: Ortam değişkenleri
            timeout: Zaman aşımı (saniye)

        Returns:
            Process ID (p_id formatında)
        """
        pid_key = f"p_{int(time.time()*1000) % 10000000}"
        log_path = self._log_yolu(pid_key)

        # Ortam değişkenleri
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)

        try:
            # shell=True bilerek kullanılır — komut string olarak gelir
            # ve kullanıcının terminal deneyimi için shell yorumlaması gerekir
            if not isinstance(komut, str):
                komut_str = " ".join(str(k) for k in komut)
            else:
                komut_str = komut
            with open(log_path, "w", encoding="utf-8") as log_file:
                proc = subprocess.Popen(
                    komut_str,
                    shell=True,  # nosec B602 — shell gereklidir, komut string olarak gelir
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    cwd=calisma_dizini if calisma_dizini else None,
                    env=proc_env,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )

            self._procler[pid_key] = {
                "pid": proc.pid,
                "komut": komut,
                "baslama": datetime.now().isoformat(),
                "durum": "calisiyor",
                "calisma_dizini": calisma_dizini,
                "timeout": timeout,
                "cikis_kodu": None,
                "bitis": None,
            }
            self._kaydet()

            # Timeout watcher
            if timeout:
                def _timeout_watcher():
                    time.sleep(timeout)
                    if self._procler.get(pid_key, {}).get("durum") == "calisiyor":
                        self.durdur(pid_key)

                t = threading.Thread(target=_timeout_watcher, daemon=True)
                t.start()

            return pid_key

        except Exception as e:
            self._procler[pid_key] = {
                "pid": 0,
                "komut": komut,
                "baslama": datetime.now().isoformat(),
                "durum": "hata",
                "hata": str(e),
                "cikis_kodu": -1,
                "bitis": datetime.now().isoformat(),
            }
            self._kaydet()
            return pid_key

    def durum(self, pid_key: str) -> Dict:
        """Process durumunu kontrol eder."""
        if pid_key not in self._procler:
            return {"durum": "bulunamadi", "error": f"Process bulunamadı: {pid_key}"}

        info = self._procler[pid_key]

        # Hala çalışıyor mu kontrol et
        if info["durum"] == "calisiyor" and info.get("pid"):
            try:
                import ctypes
                if os.name == "nt":
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.OpenProcess(0x1000, False, info["pid"])  # PROCESS_QUERY_LIMITED_INFORMATION
                    if handle:
                        exit_code = ctypes.c_ulong()
                        if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                            if exit_code.value != 259:  # STILL_ACTIVE
                                info["durum"] = "bitti"
                                info["cikis_kodu"] = exit_code.value
                                info["bitis"] = datetime.now().isoformat()
                                self._kaydet()
                        kernel32.CloseHandle(handle)
                else:
                    os.kill(info["pid"], 0)  # Sinyal 0: sadece kontrol
            except (ProcessLookupError, OSError):
                info["durum"] = "bitti"
                info["cikis_kodu"] = -1
                info["bitis"] = datetime.now().isoformat()
                self._kaydet()

        return info

    def log(self, pid_key: str, son_satir: int = 100) -> str:
        """Process log'unu okur."""
        log_path = self._log_yolu(pid_key)
        if not log_path.exists():
            return f"[Log]: Log dosyası bulunamadı: {pid_key}"

        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if son_satir > 0:
                lines = lines[-son_satir:]
            return "\n".join(lines)
        except Exception as e:
            return f"[Log Hatası]: {e}"

    def durdur(self, pid_key: str) -> bool:
        """Process'i durdurur."""
        if pid_key not in self._procler:
            return False

        info = self._procler[pid_key]
        if info["durum"] != "calisiyor":
            return False

        pid = info.get("pid", 0)
        if pid:
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                   capture_output=True, timeout=10)
                else:
                    os.kill(pid, 9)
            except Exception:
                pass

        info["durum"] = "durduruldu"
        info["bitis"] = datetime.now().isoformat()
        self._kaydet()
        return True

    def listele(self, durum: Optional[str] = None) -> List[Dict]:
        """Process listesi."""
        sonuc = []
        for pid_key, info in self._procler.items():
            if durum and info.get("durum") != durum:
                continue
            sonuc.append({"id": pid_key, **info})

        sonuc.sort(key=lambda x: x.get("baslama", ""), reverse=True)
        return sonuc

    def temizle(self, eski_saat: int = 24) -> int:
        """Eski process kayıtlarını temizler."""
        simdi = time.time()
        silinen = 0

        for pid_key in list(self._procler.keys()):
            info = self._procler[pid_key]
            if info.get("durum") != "calisiyor":
                baslama = info.get("baslama", "")
                if baslama:
                    try:
                        bt = datetime.fromisoformat(baslama).timestamp()
                        if (simdi - bt) > eski_saat * 3600:
                            del self._procler[pid_key]
                            # Log dosyasını da sil
                            log_path = self._log_yolu(pid_key)
                            if log_path.exists():
                                log_path.unlink()
                            silinen += 1
                    except Exception:
                        pass

        self._kaydet()
        return silinen


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> ProcessManager:
    global _mgr
    if _mgr is None:
        _mgr = ProcessManager()
    return _mgr


def run(islem: str = "listele", pid: str = "", komut: str = "",
        calisma_dizini: str = "", timeout: int = 0, son_satir: int = 100) -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: baslat/durum/log/durdur/listele/temizle
    """
    mgr = _get_mgr()

    if islem == "baslat":
        if not komut:
            return "[Hata]: komut parametresi gerekli."
        pid_key = mgr.baslat(komut, calisma_dizini=calisma_dizini,
                             timeout=timeout if timeout > 0 else None)
        return f"🚀 Process başlatıldı: {pid_key} (komut: {komut})"

    elif islem == "durum":
        if not pid:
            return "[Hata]: pid parametresi gerekli."
        d = mgr.durum(pid)
        if d.get("error"):
            return f"[Hata]: {d['error']}"
        return f"📊 {pid}: {d.get('durum', '?')} | PID: {d.get('pid', '?')} | Komut: {d.get('komut', '?')}"

    elif islem == "log":
        if not pid:
            return "[Hata]: pid parametresi gerekli."
        return mgr.log(pid, son_satir=son_satir)

    elif islem == "durdur":
        if not pid:
            return "[Hata]: pid parametresi gerekli."
        mgr.durdur(pid)
        return f"🛑 Process durduruldu: {pid}"

    elif islem == "temizle":
        silinen = mgr.temizle()
        return f"🧹 {silinen} eski process kaydı temizlendi."

    else:  # listele
        procler = mgr.listele()
        if not procler:
            return "📋 Aktif process yok."

        satirlar = []
        for p in procler:
            durum_emoji = {"calisiyor": "🔄", "bitti": "✅", "hata": "❌", "durduruldu": "🛑"}.get(p["durum"], "❓")
            satirlar.append(f"{durum_emoji} [{p['id']}] PID:{p.get('pid','?')} | {p.get('komut','?')[:60]}")

        return "📋 Process Listesi:\n" + "\n".join(satirlar)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python process_tool.py <islem> [parametreler]")
        sys.exit(1)
    print(run(islem=sys.argv[1], komut=sys.argv[2] if len(sys.argv) > 2 else ""))
