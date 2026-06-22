# -*- coding: utf-8 -*-
"""ReYMeN_cli/gateway.py — Gateway yonetimi CLI.

Gateway servislerini listeleme, durum kontrolu, yeniden baslatma,
test etme ve log goruntuleme islemleri.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _gateway_pid_dosyasi() -> Path:
    return PROJE_KOK / ".gateway.pid"


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
    """Gateway CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, status, restart, test, log
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "status", "restart", "test", "log"],
                            help="Yapilacak islem (list|status|restart|test|log)")
    alt_parser.add_argument("--tail", type=int, default=50,
                            help="Gosterilecek son satir sayisi (log icin)")


def calistir(args):
    """Gateway komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "list":
            print("[Gateway] Kayitli gateway servisleri:")
            servisler = {
                "Telegram Bot": _env_oku("TELEGRAM_BOT_TOKEN", "") != "",
                "Web UI": True,
                "GatewayRunner": True,
            }
            for servis, durum in servisler.items():
                if durum:
                    print(f"  + {servis}: Hazir")
                else:
                    print(f"  ! {servis}: Ayarlanmamis")
            print(f"\n  Port: 5000 (varsayilan)")

        elif islem == "status":
            print("[Gateway] Gateway durumu:")
            pid_yolu = _gateway_pid_dosyasi()
            if pid_yolu.exists():
                with open(str(pid_yolu)) as f:
                    pid = f.read().strip()
                try:
                    if sys.platform == "win32":
                        result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                                               capture_output=True, text=True)
                        calisiyor = str(pid) in result.stdout
                    else:
                        os.kill(int(pid), 0)
                        calisiyor = True
                    if calisiyor:
                        print(f"  + Gateway PID {pid}: Calisiyor")
                    else:
                        print(f"  ! Gateway PID {pid}: Calismiyor")
                except (OSError, ValueError):
                    print(f"  ! Gateway PID {pid}: Bulunamadi")
            else:
                print("  ! Gateway calismiyor (PID dosyasi yok)")

            token = _env_oku("TELEGRAM_BOT_TOKEN", "")
            chat_id = _env_oku("TELEGRAM_CHAT_ID", "")
            if token:
                print(f"  + Telegram Token: Mevcut")
            if chat_id:
                print(f"  + Telegram Chat ID: {chat_id}")
            try:
                import flask
                print(f"  + Web UI: Flask hazir")
            except ImportError:
                print(f"  ! Web UI: Flask yuklu degil")

        elif islem == "restart":
            print("[Gateway] Gateway yeniden baslatiliyor...")
            pid_yolu = _gateway_pid_dosyasi()
            if pid_yolu.exists():
                with open(str(pid_yolu)) as f:
                    eski_pid = f.read().strip()
                try:
                    os.kill(int(eski_pid), 9)
                    print(f"  + PID {eski_pid} durduruldu.")
                except (OSError, ValueError):
                    print(f"  ! PID {eski_pid} bulunamadi.")
                pid_yolu.unlink(missing_ok=True)
            print("  + Gateway yeniden baslatma hazirligi tamam.")
            sys.path.insert(0, str(PROJE_KOK))
            try:
                from gateway_runner import GatewayRunner
                runner = GatewayRunner()
                print(f"  + Gateway baslatildi.")
            except ImportError as e:
                print(f"  ! Gateway baslatilamadi: {e}")

        elif islem == "test":
            print("[Gateway] Gateway testi yapiliyor...")
            token = _env_oku("TELEGRAM_BOT_TOKEN", "")
            if token:
                import urllib.request
                import urllib.error
                try:
                    url = f"https://api.telegram.org/bot{token}/getMe"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read().decode())
                        if data.get("ok"):
                            bot_info = data.get("result", {})
                            print(f"  + Telegram Baglantisi: Basarili")
                            print(f"  + Bot: @{bot_info.get('username', '?')}")
                        else:
                            print(f"  ! Telegram API Hatasi: {data}")
                except Exception as e:
                    print(f"  ! Telegram Baglantisi: Basarisiz - {e}")
            else:
                print(f"  ! TELEGRAM_BOT_TOKEN ayarlanmamis")
            try:
                import flask
                print(f"  + Flask: Calisiyor")
            except ImportError:
                print(f"  ! Flask: Yuklu degil")
            try:
                import requests
                print(f"  + requests: Calisiyor")
            except ImportError:
                print(f"  ! requests: Yuklu degil")

        elif islem == "log":
            log_yolu = PROJE_KOK / "gateway.log"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    satirlar = f.readlines()
                tail = args.tail
                print(f"[Gateway] Son {tail} satir log:")
                for satir in satirlar[-tail:]:
                    print(f"  {satir.rstrip()}")
            else:
                print("[Gateway] Log dosyasi bulunamadi.")

    except Exception as e:
        print(f"[Gateway] Beklenmeyen hata: {e}")
