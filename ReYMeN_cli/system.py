# -*- coding: utf-8 -*-
"""ReYMeN_cli/system.py — Sistem CLI.

Sistem bilgisi, guncelleme, temizlik, ortam degiskenleri
ve sistem teshisi islemleri.
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _env_oku(anahtar: str, varsayilan: str = "") -> str:
    """.env dosyasindan anahtar degerini oku."""
    env_yolu = PROJE_KOK / ".env"
    if not env_yolu.exists():
        return varsayilan
    with open(str(env_yolu), "r", encoding="utf-8") as f:
        for satir in f:
            satir_stripped = satir.strip()
            if satir_stripped.startswith("#") or "=" not in satir_stripped:
                continue
            k, v = satir_stripped.split("=", 1)
            if k.strip() == anahtar:
                return v.strip().strip('"').strip("'")
    return varsayilan


def kaydet(alt_parser):
    """System CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: info, update, cleanup, env, doctor
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["info", "update", "cleanup", "env", "doctor"],
                            help="Yapilacak islem (info|update|cleanup|env|doctor)")


def calistir(args):
    """System komutunu calistir."""
    try:
        islem = args.islem or "info"

        if islem == "info":
            print("[System] ReYMeN Sistem Bilgisi:")
            print(f"  Platform: {platform.platform()}")
            print(f"  Sistem: {sys.platform}")
            print(f"  Python: {sys.version}")
            print(f"  Makine: {platform.machine()}")
            print(f"  Islemci: {platform.processor()}")
            print(f"  Node: {platform.node()}")
            print(f"  Proje: {PROJE_KOK}")
            try:
                toplam, kullanilan, bos = shutil.disk_usage(str(PROJE_KOK))
                print(f"  Disk: Toplam {toplam / (1024**3):.1f} GB, Bos {bos / (1024**3):.1f} GB")
            except Exception:
                pass
            pyc_sayisi = len(list(PROJE_KOK.rglob("*.pyc")))
            print(f"  .pyc dosyalari: {pyc_sayisi}")
            try:
                git_hash = subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=str(PROJE_KOK), stderr=subprocess.DEVNULL, text=True
                ).strip()
                print(f"  Git: {git_hash}")
            except Exception:
                pass
            print(f"  Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        elif islem == "update":
            print("[System] Guncelleme kontrolu yapiliyor...")
            try:
                import urllib.request
                import json
                req = urllib.request.Request(
                    "https://api.github.com/repos/nousresearch/ReYMeN-agent/releases/latest",
                    headers={"User-Agent": "ReYMeN-CLI"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    print(f"  Son surum: {data.get('tag_name', '?')}")
                    print(f"  Tarih: {data.get('published_at', '?')}")
                    print(f"  URL: {data.get('html_url', '?')}")
            except Exception as e:
                print(f"  Guncelleme kontrol edilemedi: {e}")
            try:
                if (PROJE_KOK / ".git").exists():
                    result = subprocess.run(
                        ["git", "pull"],
                        cwd=str(PROJE_KOK), capture_output=True, text=True
                    )
                    print(f"  Git: {result.stdout.strip()}")
                    if result.stderr:
                        print(f"  Hata: {result.stderr.strip()}")
            except Exception as e:
                print(f"  Git guncellemesi yapilamadi: {e}")

        elif islem == "cleanup":
            print("[System] Temizlik baslatiliyor...")
            toplam_temizlik = 0
            for pyc in PROJE_KOK.rglob("*.pyc"):
                try:
                    boyut = pyc.stat().st_size
                    pyc.unlink()
                    toplam_temizlik += boyut
                except Exception:
                    continue
            for pycache in PROJE_KOK.rglob("__pycache__"):
                if pycache.is_dir():
                    try:
                        shutil.rmtree(str(pycache))
                    except Exception:
                        continue
            print(f"  + .pyc dosyalari temizlendi: {toplam_temizlik}B silindi")
            gecici_dosyalar = [".temp_skill_clone", "node_modules"]
            for d in gecici_dosyalar:
                yol = PROJE_KOK / d
                if yol.exists():
                    try:
                        boyut = sum(f.stat().st_size for f in yol.rglob("*")) if yol.is_dir() else yol.stat().st_size
                        shutil.rmtree(str(yol)) if yol.is_dir() else yol.unlink()
                        print(f"  + {d} temizlendi ({boyut}B)")
                        toplam_temizlik += boyut
                    except Exception as e:
                        print(f"  ! {d} temizlenemedi: {e}")
            print(f"[System] Temizlik tamam. Toplam {toplam_temizlik}B bosaltildi.")

        elif islem == "env":
            print("[System] Ortam degiskenleri (.env):")
            env_yolu = PROJE_KOK / ".env"
            if env_yolu.exists():
                hassas_anahtarlar = ["API_KEY", "TOKEN", "SECRET", "PASSWORD"]
                with open(str(env_yolu), "r", encoding="utf-8") as f:
                    for satir in f:
                        satir_stripped = satir.strip()
                        if not satir_stripped or satir_stripped.startswith("#"):
                            continue
                        if "=" in satir_stripped:
                            k, v = satir_stripped.split("=", 1)
                            gizli = any(h in k.upper() for h in hassas_anahtarlar)
                            goruntu = (v[:4] + "****") if gizli and v else (v or "(bos)")
                            print(f"  {k.strip()} = {goruntu}")
            else:
                print("  .env dosyasi bulunamadi.")
            print(f"\n[System] Sistem PATH bilgisi:")
            for p in os.environ.get("PATH", "").split(os.pathsep):
                if "python" in p.lower() or "ReYMeN" in p.lower() or "reyment" in p.lower():
                    print(f"  + {p}")

        elif islem == "doctor":
            print("[System] Sistem teshisi:")
            sorunlar = []
            gerekli_dosyalar = ["main.py", "motor.py", "beyin.py", "setup.py"]
            eksik = [d for d in gerekli_dosyalar if not (PROJE_KOK / d).exists()]
            if eksik:
                print(f"  ! Eksik moduller: {', '.join(eksik)}")
                sorunlar.extend(eksik)
            else:
                print(f"  + Temel moduller mevcut")
            env_yolu = PROJE_KOK / ".env"
            if env_yolu.exists():
                print(f"  + .env dosyasi mevcut")
            else:
                print(f"  ! .env dosyasi yok")
                sorunlar.append(".env")
            ReYMeN_yolu = PROJE_KOK / ".ReYMeN"
            if ReYMeN_yolu.exists():
                print(f"  + .ReYMeN/ dizini mevcut")
            else:
                print(f"  ! .ReYMeN/ dizini yok")
                sorunlar.append(".ReYMeN")
            kutuphaneler = ["flask", "requests"]
            for k in kutuphaneler:
                try:
                    __import__(k.replace("-", "_"))
                    print(f"  + {k} yuklu")
                except ImportError:
                    print(f"  ! {k} yuklu degil")
                    sorunlar.append(k)
            if sorunlar:
                print(f"\n  {len(sorunlar)} sorun tespit edildi:")
                for s in sorunlar:
                    print(f"    * {s}")
            else:
                print(f"\n  Sistem saglikli.")

    except Exception as e:
        print(f"[System] Beklenmeyen hata: {e}")
