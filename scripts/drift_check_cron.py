#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drift_check_cron.py — Her cycle başında otomatik duplicate/drift kontrolü.

Çalışma:
  1. duplicate_module_detector.py ile proje taranır
  2. Sonuç .ReYMeN/raporlar/drift-YYYY-MM-DD.json'a kaydedilir
  3. Özet terminal'e yazdırılır
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
DETECTOR = ROOT / "scripts" / "duplicate_module_detector.py"
RAPOR_DIR = ROOT / ".ReYMeN" / "raporlar"
RAPOR_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    tarih = datetime.now().strftime("%Y-%m-%d")
    rapor_yolu = RAPOR_DIR / f"drift-{tarih}.json"

    print(f"[drift-check] {datetime.now().strftime('%H:%M:%S')} — tarama basliyor...")

    import os as _os
    env = _os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    sonuc = subprocess.run(
        [sys.executable, str(DETECTOR), str(ROOT), "--format", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
        timeout=60,
        env=env,
    )

    # exit 0 = temiz, exit 1 = drift bulundu (beklenen), diger = gercek hata
    if sonuc.returncode not in (0, 1):
        print(f"[drift-check] HATA: exit={sonuc.returncode}\n{sonuc.stderr[:300]}")
        return 1

    cikti = sonuc.stdout.strip() or sonuc.stderr.strip()

    # JSON çıktısını ayrıştır
    try:
        veri = json.loads(cikti)
        toplam = veri.get("toplam_drift", "?")
    except (json.JSONDecodeError, ValueError):
        toplam = "?"
        veri = {"ham_cikti": cikti[:2000]}

    # Rapor dosyasına kaydet
    with open(rapor_yolu, "w", encoding="utf-8") as f:
        json.dump({
            "tarih": datetime.now().isoformat(),
            "toplam_drift": toplam,
            "veri": veri,
        }, f, ensure_ascii=False, indent=2)

    print(f"[drift-check] TAMAMLANDI — {toplam} drift bulgusu → {rapor_yolu.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
