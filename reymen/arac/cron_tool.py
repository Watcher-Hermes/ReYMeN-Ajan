# -*- coding: utf-8 -*-
"""
cron_tool.py — Zamanlanmış görev sistemi.

Hermes Agent cronjob_tool karşılığı.
Cron benzeri zamanlanmış görevler oluştur, listele, durdur.

Dosya: .ReYMeN/cron_jobs.json

Kurulum: pip install schedule (opsiyonel)

Kullanım:
    from reymen.arac.cron_tool import CronManager
    mgr = CronManager()
    mgr.ekle("yedekle", "0 3 * * *", "python yedekle.py")
    mgr.listele()
"""

import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any


class CronJob:
    """Tek bir cron job tanımı."""

    def __init__(self, job_id: str, ad: str, komut: str, zamanlama: str,
                 aciklama: str = "", aktif: bool = True, son_calisma: Optional[str] = None):
        self.id = job_id
        self.ad = ad
        self.komut = komut
        self.zamanlama = zamanlama  # "*/5 * * * *" veya "30m" veya "every 2h"
        self.aciklama = aciklama
        self.aktif = aktif
        self.son_calisma = son_calisma
        self._sonraki_calisma = self._sonraki_hesapla()

    def _sonraki_calisma_dakika(self) -> int:
        """Zamanlama stringinden dakika cinsinden aralık döner."""
        z = self.zamanlama.strip()

        # "30m", "5m", "1h", "2h" formatı
        m = re.match(r'^(\d+)(m|h|d)$', z)
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            return val * {"m": 1, "h": 60, "d": 1440}[unit]

        # "every 30m", "every 2h" formatı
        m = re.match(r'^every\s+(\d+)(m|h|d)$', z, re.I)
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            return val * {"m": 1, "h": 60, "d": 1440}[unit]

        # Basit dakika
        m = re.match(r'^(\d+)$', z)
        if m:
            return int(m.group(1))

        # Cron formatı: "*/5 * * * *" → 5 dakika
        m = re.match(r'^\*/(\d+)\s+\*\s+\*\s+\*\s+\*$', z)
        if m:
            return int(m.group(1))

        return 60  # Varsayılan 1 saat

    def _sonraki_hesapla(self) -> float:
        """Sonraki çalışma zamanını hesaplar."""
        dakika = self._sonraki_calisma_dakika()
        return time.time() + dakika * 60

    def calis_zamani_mi(self) -> bool:
        """Şimdi çalışması gerekiyor mu?"""
        if not self.aktif:
            return False
        return time.time() >= self._sonraki_calisma

    def calistirildi(self):
        """Çalıştırıldı olarak işaretle."""
        self.son_calisma = datetime.now().isoformat()
        self._sonraki_calisma = self._sonraki_hesapla()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "ad": self.ad,
            "komut": self.komut,
            "zamanlama": self.zamanlama,
            "aciklama": self.aciklama,
            "aktif": self.aktif,
            "son_calisma": self.son_calisma,
        }


class CronManager:
    """Zamanlanmış görev yöneticisi."""

    def __init__(self, dosya: Optional[str] = None):
        self._dosya = Path(dosya) if dosya else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "cron_jobs.json"
        )
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, CronJob] = {}
        self._calisiyor = False
        self._thread: Optional[threading.Thread] = None
        self._yukle()

    def _yukle(self):
        """Job'ları dosyadan yükler."""
        if not self._dosya.exists():
            return
        try:
            data = json.loads(self._dosya.read_text(encoding="utf-8"))
            for j in data:
                job = CronJob(**j)
                self._jobs[job.id] = job
        except Exception:
            pass

    def _kaydet(self):
        """Job'ları dosyaya kaydeder."""
        data = [j.to_dict() for j in self._jobs.values()]
        self._dosya.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _id_uret(self) -> str:
        return f"cron_{int(time.time()*1000) % 10000000}"

    def ekle(self, ad: str, zamanlama: str, komut: str,
             aciklama: str = "", aktif: bool = True) -> CronJob:
        """Yeni cron job ekler."""
        job_id = self._id_uret()
        job = CronJob(job_id, ad, komut, zamanlama, aciklama, aktif)
        self._jobs[job_id] = job
        self._kaydet()
        return job

    def kaldir(self, job_id: str) -> bool:
        """Job'ı kaldırır."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            self._kaydet()
            return True
        return False

    def duraklat(self, job_id: str) -> bool:
        """Job'ı duraklatır."""
        if job_id in self._jobs:
            self._jobs[job_id].aktif = False
            self._kaydet()
            return True
        return False

    def devam(self, job_id: str) -> bool:
        """Job'ı devam ettirir."""
        if job_id in self._jobs:
            self._jobs[job_id].aktif = True
            self._kaydet()
            return True
        return False

    def listele(self) -> List[Dict]:
        """Tüm job'ları listeler."""
        return [j.to_dict() for j in self._jobs.values()]

    def calistir(self, job_id: str) -> str:
        """Job'ı manuel olarak çalıştırır."""
        if job_id not in self._jobs:
            return f"[Hata]: Job bulunamadı: {job_id}"

        job = self._jobs[job_id]
        try:
            komut_list = shlex.split(job.komut)
            result = subprocess.run(
                komut_list, shell=False, capture_output=True, text=True,
                timeout=300, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )  # nosec B603 — shell=False, shlex.split ile güvenli
            job.calistirildi()
            self._kaydet()

            out = result.stdout.strip()
            err = result.stderr.strip()
            cikti = f"✅ [{job.ad}] çalıştırıldı (çıkış kodu: {result.returncode})\n"
            if out:
                cikti += f"Çıktı:\n{out[:2000]}\n"
            if err:
                cikti += f"Hata:\n{err[:1000]}\n"
            return cikti

        except subprocess.TimeoutExpired:
            return f"[Hata]: [{job.ad}] zaman aşımı (300s)."
        except Exception as e:
            return f"[Hata]: [{job.ad}] çalıştırma hatası: {e}"

    def _zamanlayici_dongusu(self):
        """Arka plan zamanlayıcı döngüsü."""
        while self._calisiyor:
            for job in list(self._jobs.values()):
                if job.calis_zamani_mi():
                    try:
                        komut_list = shlex.split(job.komut)
                        subprocess.run(
                            komut_list, shell=False, capture_output=True, timeout=300,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                        )  # nosec B603
                        job.calistirildi()
                        self._kaydet()
                    except Exception:
                        pass
            time.sleep(30)  # Her 30 saniyede kontrol

    def baslat_zamanlayici(self):
        """Arka plan zamanlayıcıyı başlatır."""
        if self._calisiyor:
            return "Zamanlayıcı zaten çalışıyor."
        self._calisiyor = True
        self._thread = threading.Thread(target=self._zamanlayici_dongusu, daemon=True)
        self._thread.start()
        return "⏰ Zamanlayıcı başlatıldı."

    def durdur_zamanlayici(self):
        """Arka plan zamanlayıcıyı durdurur."""
        self._calisiyor = False
        return "🛑 Zamanlayıcı durduruldu."


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> CronManager:
    global _mgr
    if _mgr is None:
        _mgr = CronManager()
    return _mgr


def run(islem: str = "listele", job_id: str = "", ad: str = "",
        zamanlama: str = "", komut: str = "", aciklama: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: ekle/kaldir/duraklat/devam/calistir/listele/baslat/durdur
    """
    mgr = _get_mgr()

    if islem == "ekle":
        if not ad or not zamanlama or not komut:
            return "[Hata]: ad, zamanlama ve komut gerekli."
        job = mgr.ekle(ad, zamanlama, komut, aciklama=aciklama)
        return f"✅ Cron job eklendi: [{job.id}] {job.ad} | {job.zamanlama}"

    elif islem == "kaldir":
        if not job_id:
            return "[Hata]: job_id gerekli."
        mgr.kaldir(job_id)
        return f"🗑️ Job kaldırıldı: {job_id}"

    elif islem == "duraklat":
        if not job_id:
            return "[Hata]: job_id gerekli."
        mgr.duraklat(job_id)
        return f"⏸️ Job duraklatıldı: {job_id}"

    elif islem == "devam":
        if not job_id:
            return "[Hata]: job_id gerekli."
        mgr.devam(job_id)
        return f"▶️ Job devam ediyor: {job_id}"

    elif islem == "calistir":
        if not job_id:
            return "[Hata]: job_id gerekli."
        return mgr.calistir(job_id)

    elif islem == "baslat":
        return mgr.baslat_zamanlayici()

    elif islem == "durdur":
        return mgr.durdur_zamanlayici()

    else:  # listele
        jobs = mgr.listele()
        if not jobs:
            return "📋 Cron job yok."
        satirlar = []
        for j in jobs:
            emoji = "✅" if j["aktif"] else "⏸️"
            son = j.get("son_calisma", "hiç")
            satirlar.append(f"{emoji} [{j['id']}] {j['ad']} | {j['zamanlama']} | Son: {son}")
        return "⏰ Cron Jobs:\n" + "\n".join(satirlar)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python cron_tool.py <islem> [parametreler]")
        sys.exit(1)
    print(run(islem=sys.argv[1], ad=sys.argv[2] if len(sys.argv) > 2 else ""))
