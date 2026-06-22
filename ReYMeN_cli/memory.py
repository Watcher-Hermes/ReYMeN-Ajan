# -*- coding: utf-8 -*-
"""ReYMeN_cli/memory.py — Hafiza yonetimi CLI.

Hafiza istatistikleri, temizleme, optimize etme, yedekleme
ve geri yukleme islemleri.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
MEM_DIR = PROJE_KOK / ".ReYMeN" / "memories"


def _mem_dosyalari() -> list:
    """Hafiza dosyalarini listele."""
    if not MEM_DIR.exists():
        return []
    return [f for f in MEM_DIR.iterdir() if f.is_file()]


def kaydet(alt_parser):
    """Memory CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: stats, clear, optimize, backup, restore
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["stats", "clear", "optimize", "backup", "restore"],
                            help="Yapilacak islem (stats|clear|optimize|backup|restore)")
    alt_parser.add_argument("--force", "-f", action="store_true",
                            help="Onay sormadan islem yap")
    alt_parser.add_argument("--file", type=str, default=None,
                            help="Dosya adi (backup/restore)")


def calistir(args):
    """Memory komutunu calistir."""
    try:
        islem = args.islem or "stats"
        MEM_DIR.mkdir(parents=True, exist_ok=True)

        if islem == "stats":
            dosyalar = _mem_dosyalari()
            print(f"[Memory] Hafiza istatistikleri:")
            print(f"  Klasor: {MEM_DIR}")
            print(f"  Dosya sayisi: {len(dosyalar)}")
            toplam_boyut = 0
            for d in dosyalar:
                boyut = d.stat().st_size
                toplam_boyut += boyut
                print(f"    + {d.name}: {boyut} B")
            print(f"  Toplam: {toplam_boyut} B ({toplam_boyut / 1024:.2f} KB)")
            print(f"  Son guncelleme: {datetime.fromtimestamp(max(d.stat().st_mtime for d in dosyalar)).strftime('%d.%m.%Y %H:%M:%S') if dosyalar else 'Yok'}")

        elif islem == "clear":
            if not args.force:
                print("[Memory] Uyari: Bu islem tum hafiza dosyalarini temizleyecek!")
                print("[Memory] --force ile onaylayin.")
                return
            dosyalar = _mem_dosyalari()
            for d in dosyalar:
                d.unlink()
                print(f"  + Silindi: {d.name}")
            for varsayilan in ["MEMORY.md", "USER.md"]:
                yeni_dosya = MEM_DIR / varsayilan
                with open(str(yeni_dosya), "w", encoding="utf-8") as f:
                    f.write(f"# {varsayilan}\n\n_Hafiza {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} tarihinde sifirlandi._\n")
                print(f"  + Olusturuldu: {varsayilan}")
            print("[Memory] Hafiza sifirlandi.")

        elif islem == "optimize":
            dosyalar = _mem_dosyalari()
            toplam_tasarruf = 0
            for d in dosyalar:
                try:
                    with open(str(d), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    eski_boyut = len(icerik)
                    satirlar = [s for s in icerik.split("\n") if s.strip()]
                    yeni_icerik = "\n".join(satirlar)
                    with open(str(d), "w", encoding="utf-8") as f:
                        f.write(yeni_icerik)
                    yeni_boyut = len(yeni_icerik)
                    tasarruf = eski_boyut - yeni_boyut
                    toplam_tasarruf += tasarruf
                    if tasarruf > 0:
                        print(f"  + {d.name}: {eski_boyut}B -> {yeni_boyut}B ({tasarruf}B tasarruf)")
                except Exception as e:
                    print(f"  ! {d.name}: optimize edilemedi - {e}")
            print(f"[Memory] Optimizasyon tamam. Toplam {toplam_tasarruf}B tasarruf edildi.")

        elif islem == "backup":
            dosya_adi = args.file or f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            hedef_zip = PROJE_KOK / "backups" / dosya_adi
            (PROJE_KOK / "backups").mkdir(exist_ok=True)
            if MEM_DIR.exists():
                shutil.make_archive(str(hedef_zip), "zip", str(MEM_DIR))
                print(f"[Memory] Hafiza yedeklendi: {hedef_zip}.zip")
            else:
                print("[Memory] Yedeklenecek hafiza bulunamadi.")

        elif islem == "restore":
            dosya_adi = args.file
            if not dosya_adi:
                backups_dir = PROJE_KOK / "backups"
                if backups_dir.exists():
                    yedekler = list(backups_dir.glob("memory_backup*.zip"))
                    if yedekler:
                        son_yedek = max(yedekler, key=os.path.getmtime)
                        dosya_adi = str(son_yedek)
                        print(f"[Memory] Son yedek bulundu: {son_yedek.name}")
                    else:
                        print("[Memory] Yedek bulunamadi.")
                        return
                else:
                    print("[Memory] backups/ klasoru bulunamadi.")
                    return
            kaynak_zip = Path(dosya_adi)
            if not kaynak_zip.exists():
                kaynak_zip = PROJE_KOK / "backups" / dosya_adi
            if not kaynak_zip.exists():
                kaynak_zip = PROJE_KOK / "backups" / f"{dosya_adi}.zip"
            if not kaynak_zip.exists():
                print(f"[Memory] Yedek dosyasi bulunamadi: {dosya_adi}")
                return
            if MEM_DIR.exists():
                shutil.rmtree(str(MEM_DIR))
            MEM_DIR.mkdir(parents=True)
            shutil.unpack_archive(str(kaynak_zip), str(MEM_DIR))
            print(f"[Memory] Hafiza geri yuklendi: {kaynak_zip}")

    except Exception as e:
        print(f"[Memory] Beklenmeyen hata: {e}")
