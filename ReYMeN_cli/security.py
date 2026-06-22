# -*- coding: utf-8 -*-
"""ReYMeN_cli/security.py — Guvenlik CLI.

Guvenlik denetimi, tarama, kontrol, raporlama ve duzeltme islemleri.
"""

import hashlib
import json
import os
import stat
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _hash_dosyasi(dosya_yolu: Path) -> str:
    """Dosyanin SHA256 hash'ini hesapla."""
    h = hashlib.sha256()
    try:
        with open(str(dosya_yolu), "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def _izin_kontrolu(dosya_yolu: Path) -> list:
    """Dosya izinlerini kontrol et."""
    sorunlar = []
    try:
        mod = os.stat(str(dosya_yolu)).st_mode
        if sys.platform != "win32" and mod & stat.S_IWOTH:
            sorunlar.append("Diger kullanicilar yazma iznine sahip")
    except Exception:
        pass
    return sorunlar


def kaydet(alt_parser):
    """Security CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: audit, scan, check, report, fix
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["audit", "scan", "check", "report", "fix"],
                            help="Yapilacak islem (audit|scan|check|report|fix)")
    alt_parser.add_argument("--target", type=str, default=None,
                            help="Hedef dosya/dizin")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Rapor cikti dosyasi")


def calistir(args):
    """Security komutunu calistir."""
    try:
        islem = args.islem or "check"

        if islem == "audit":
            print("[Security] Guvenlik denetimi baslatiliyor...")
            bulgular = []
            hassas_dosyalar = [".env", "config.json", "credentials.json", "token.json"]
            for dosya in hassas_dosyalar:
                dosya_yolu = PROJE_KOK / dosya
                if dosya_yolu.exists():
                    izin_sorunlari = _izin_kontrolu(dosya_yolu)
                    bulgular.append({
                        "dosya": dosya,
                        "hash": _hash_dosyasi(dosya_yolu)[:16],
                        "boyut": dosya_yolu.stat().st_size,
                        "sorunlar": izin_sorunlari,
                    })
            print(f"  {len(bulgular)} hassas dosya bulundu.")
            for b in bulgular:
                print(f"  + {b['dosya']} ({b['boyut']}B, hash: {b['hash']})")
                for s in b["sorunlar"]:
                    print(f"    ! {s}")
            print("[Security] Denetim tamam.")

        elif islem == "scan":
            print("[Security] Dosya taramasi yapiliyor...")
            hedef = args.target or str(PROJE_KOK)
            hedef_yol = Path(hedef)
            if not hedef_yol.exists():
                print(f"[Security] Hedef bulunamadi: {hedef}")
                return
            py_dosyalari = list(hedef_yol.rglob("*.py"))
            supheli = 0
            for py_dosya in py_dosyalari:
                try:
                    with open(str(py_dosya), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    supheli_kalip = [
                        "exec(", "eval(", "__import__(", "compile(",
                        "subprocess.call", "os.system", "base64.b64decode",
                    ]
                    for kalip in supheli_kalip:
                        if kalip in icerik:
                            satir_no = next((i + 1 for i, s in enumerate(icerik.split("\n")) if kalip in s), 0)
                            print(f"  ? {py_dosya.relative_to(PROJE_KOK)}:{satir_no} -> {kalip}")
                            supheli += 1
                            break
                except Exception:
                    continue
            if supheli == 0:
                print(f"  {len(py_dosyalari)} dosya tarandi, supheli icerik bulunamadi.")
            else:
                print(f"  {len(py_dosyalari)} dosya tarandi, {supheli} supheli bulgu.")

        elif islem == "check":
            print("[Security] Guvenlik kontrolleri:")
            env_yolu = PROJE_KOK / ".env"
            if env_yolu.exists():
                mod = os.stat(str(env_yolu)).st_mode
                print(f"  + .env dosyasi mevcut")
            else:
                print(f"  ! .env dosyasi bulunamadi")
            git_yolu = PROJE_KOK / ".gitignore"
            if git_yolu.exists():
                with open(str(git_yolu), "r") as f:
                    gitignore = f.read()
                if ".env" in gitignore:
                    print(f"  + .env .gitignore'da belirtilmis")
                else:
                    print(f"  ! .env .gitignore'da belirtilmemis")
            else:
                print(f"  ! .gitignore bulunamadi")
            ReYMeN_yolu = PROJE_KOK / ".ReYMeN"
            if ReYMeN_yolu.exists():
                print(f"  + .ReYMeN/ dizini mevcut")
                skills_yolu = ReYMeN_yolu / "skills"
                if skills_yolu.exists():
                    print(f"  + skills/: {len(list(skills_yolu.iterdir()))} dosya")
            else:
                print(f"  ! .ReYMeN/ dizini bulunamadi")

        elif islem == "report":
            cikti = args.output or str(PROJE_KOK / "security_report.json")
            print(f"[Security] Rapor olusturuluyor: {cikti}")
            rapor = {
                "tarih": datetime.now().isoformat(),
                "proje": str(PROJE_KOK),
                "kontroller": [],
            }
            env_yolu = PROJE_KOK / ".env"
            rapor["kontroller"].append({
                "kontrol": ".env dosyasi",
                "durum": "OK" if env_yolu.exists() else "UYARI",
            })
            git_yolu = PROJE_KOK / ".gitignore"
            if git_yolu.exists():
                with open(str(git_yolu), "r") as f:
                    rapor["kontroller"].append({
                        "kontrol": ".env .gitignore'da",
                        "durum": "OK" if ".env" in f.read() else "UYARI",
                    })
            hassas_dosyalar = [".env"]
            for d in hassas_dosyalar:
                dosya_yolu = PROJE_KOK / d
                if dosya_yolu.exists():
                    rapor["kontroller"].append({
                        "kontrol": f"{d} izinleri",
                        "durum": "OK",
                        "hash": _hash_dosyasi(dosya_yolu)[:16],
                    })
            with open(cikti, "w", encoding="utf-8") as f:
                json.dump(rapor, f, indent=2, ensure_ascii=False)
            print(f"[Security] Rapor kaydedildi: {cikti}")

        elif islem == "fix":
            print("[Security] Guvenlik duzeltmeleri uygulaniyor...")
            env_yolu = PROJE_KOK / ".env"
            if env_yolu.exists():
                if sys.platform != "win32":
                    os.chmod(str(env_yolu), stat.S_IRUSR | stat.S_IWUSR)
                    print(f"  + .env izinleri duzeltildi (600)")
                else:
                    print(f"  + .env Windows'ta izin duzeltmesi gerekmiyor")
            git_yolu = PROJE_KOK / ".gitignore"
            if git_yolu.exists():
                with open(str(git_yolu), "r") as f:
                    icerik = f.read()
                if ".env" not in icerik:
                    with open(str(git_yolu), "a") as f:
                        f.write("\n# Guvenlik\n.env\n")
                    print(f"  + .env .gitignore'a eklendi")
            else:
                with open(str(git_yolu), "w") as f:
                    f.write("# ReYMeN .gitignore\n.env\n*.pyc\n__pycache__/\n.ReYMeN/\n")
                print(f"  + .gitignore olusturuldu")
            print("[Security] Duzeltmeler tamam.")

    except Exception as e:
        print(f"[Security] Beklenmeyen hata: {e}")
