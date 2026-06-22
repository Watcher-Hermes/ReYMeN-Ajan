# -*- coding: utf-8 -*-
"""ReYMeN_cli/agent.py — Ajan yonetimi CLI.

Ajan baslatma, durdurma, yeniden baslatma, durum sorgulama
ve log goruntuleme islemleri.
"""

import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _proje_yolu(alt: str = "") -> str:
    return str(PROJE_KOK / alt) if alt else str(PROJE_KOK)


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
    """Agent CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: start, stop, restart, status, logs
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "restart", "status", "logs"],
                            help="Yapilacak islem (start|stop|restart|status|logs)")
    alt_parser.add_argument("--pid", type=int, default=None,
                            help="PID (stop/restart icin)")
    alt_parser.add_argument("--tail", type=int, default=50,
                            help="Gosterilecek son satir sayisi (logs icin)")


def calistir(args):
    """Agent komutunu calistir."""
    try:
        islem = args.islem or "status"
        if islem == "start":
            print("[Agent] Ajan baslatiliyor...")
            sys.path.insert(0, _proje_yolu())
            try:
                from main import AIAgentOrchestrator, CONFIG
                agent = AIAgentOrchestrator(config=CONFIG)
                print("[Agent] Ajan baslatildi.")
            except ImportError as e:
                print(f"[Agent] Hata: main.py yuklenemedi: {e}")
        elif islem == "stop":
            pid = args.pid
            if pid:
                import os
                try:
                    os.kill(pid, 9)
                    print(f"[Agent] PID {pid} durduruldu.")
                except ProcessLookupError:
                    print(f"[Agent] PID {pid} bulunamadi.")
            else:
                pid_yolu = PROJE_KOK / ".agent.pid"
                if pid_yolu.exists():
                    with open(str(pid_yolu)) as f:
                        eski_pid = int(f.read().strip())
                    import os
                    try:
                        os.kill(eski_pid, 9)
                        print(f"[Agent] PID {eski_pid} durduruldu.")
                    except ProcessLookupError:
                        print(f"[Agent] PID {eski_pid} zaten kapali.")
                    pid_yolu.unlink(missing_ok=True)
                else:
                    print("[Agent] Calisan ajan bulunamadi.")
        elif islem == "restart":
            pid = args.pid
            if pid:
                import os
                try:
                    os.kill(pid, 9)
                    print(f"[Agent] PID {pid} durduruldu, yeniden baslatiliyor...")
                except ProcessLookupError:
                    print(f"[Agent] PID {pid} bulunamadi, baslatiliyor...")
            sys.path.insert(0, _proje_yolu())
            try:
                from main import AIAgentOrchestrator, CONFIG
                agent = AIAgentOrchestrator(config=CONFIG)
                print("[Agent] Ajan yeniden baslatildi.")
            except ImportError as e:
                print(f"[Agent] Hata: {e}")
        elif islem == "status":
            pid_yolu = PROJE_KOK / ".agent.pid"
            if pid_yolu.exists():
                with open(str(pid_yolu)) as f:
                    mevcut_pid = f.read().strip()
                import os
                try:
                    os.kill(int(mevcut_pid), 0)
                    print(f"[Agent] Ajan calisiyor (PID: {mevcut_pid})")
                except (OSError, ValueError):
                    print(f"[Agent] Ajan PID dosyasi var ama calismiyor (PID: {mevcut_pid})")
            else:
                print("[Agent] Ajan calismiyor.")
        elif islem == "logs":
            log_yolu = PROJE_KOK / "agent.log"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    satirlar = f.readlines()
                tail = args.tail
                for satir in satirlar[-tail:]:
                    print(satir.rstrip())
            else:
                print("[Agent] Log dosyasi bulunamadi.")
    except Exception as e:
        print(f"[Agent] Beklenmeyen hata: {e}")
