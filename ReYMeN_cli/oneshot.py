# -*- coding: utf-8 -*-
"""ReYMeN_cli/oneshot.py — Tek Atim Modu (One-Shot Mode).

Bir prompt alir, ReYMeN ajanini sessizce calistirir ve sonucu
dondurur. Etkilesimli dongu, banner veya ilerleme ciktisi yok.
Script icin idealdir: python reyment.py oneshot "dosya oku" --sessiz
"""

import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


class Renk:
    """ReYMeN inline Renk — ANSI renk kodlari."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    KALIN = "\033[1m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)


def oneshot_calistir(
    prompt: str,
    model: str = None,
    provider: str = None,
    toolsets: str = None,
    max_turns: int = 5,
) -> str:
    """Tek prompt ile ajani calistir ve sonucu dondur.

    Args:
        prompt: Calistirilacak prompt metni
        model: Kullanilacak model (None = varsayilan)
        provider: Kullanilacak saglayici (None = varsayilan)
        toolsets: Kullanilacak tool setleri (None = varsayilan)
        max_turns: Maksimum agent turu (varsayilan: 5)

    Returns:
        str: Ajanin urettigi sonuc metni
    """
    try:
        ortam_ayarlari = {}

        if model:
            ortam_ayarlari["ReYMeN_MODEL"] = model
        if provider:
            ortam_ayarlari["ReYMeN_PROVIDER"] = model if provider else provider

        ortam_ayarlari["ReYMeN_YOLO_MODE"] = "1"

        eski_ortam = {}
        for k, v in ortam_ayarlari.items():
            eski_ortam[k] = os.environ.get(k)
            os.environ[k] = v

        os.environ["ReYMeN_QUIET"] = "1"

        sys.path.insert(0, str(PROJE_KOK))

        try:
            from main import AIAgentOrchestrator, CONFIG

            cfg = CONFIG.copy() if hasattr(CONFIG, 'copy') else CONFIG
            if model:
                if isinstance(cfg, dict):
                    cfg["model"] = model
                else:
                    cfg.model = model

            if toolsets:
                os.environ["ReYMeN_TOOLSETS"] = toolsets

            agent = AIAgentOrchestrator(
                config=cfg,
                max_tur=max_turns,
            )

            sonuc = agent.run_conversation(prompt)
            return str(sonuc) if sonuc else "[Oneshot] Gorev tamamlandi fakat sonuc yok."

        finally:
            for k, v in eski_ortam.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            if "ReYMeN_QUIET" in os.environ:
                del os.environ["ReYMeN_QUIET"]

    except ImportError as e:
        return f"{Renk.kirmizi('[Oneshot]')} main modulu yuklenemedi: {e}"
    except Exception as e:
        return f"{Renk.kirmizi('[Oneshot]')} Beklenmeyen hata: {e}"


def kaydet(alt_parser):
    """Oneshot CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: run (tek atim)
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            default="run",
                            help="Yapilacak islem (run)")
    alt_parser.add_argument("prompt", type=str, nargs="?",
                            default="",
                            help="Calistirilacak prompt")
    alt_parser.add_argument("--model", type=str, default=None,
                            help="Model adi")
    alt_parser.add_argument("--provider", type=str, default=None,
                            help="Saglayici adi")
    alt_parser.add_argument("--toolsets", type=str, default=None,
                            help="Tool setleri (virgulle ayrilmis)")
    alt_parser.add_argument("--max-turns", type=int, default=5,
                            help="Maksimum tur sayisi (varsayilan: 5)")
    alt_parser.add_argument("--sessiz", action="store_true",
                            help="Sessiz mod — sadece sonucu yazdir")


def calistir(args):
    """Oneshot komutunu calistir."""
    try:
        prompt = args.prompt.strip() if args.prompt else ""
        if not prompt:
            print(f"{Renk.sari('[Oneshot]')} Lutfen bir prompt belirtin.")
            return

        sonuc = oneshot_calistir(
            prompt=prompt,
            model=args.model,
            provider=args.provider,
            toolsets=args.toolsets,
            max_turns=args.max_turns,
        )

        if args.sessiz:
            print(sonuc)
        else:
            print(f"\n{Renk.yesil('[Oneshot]')} Sonuc:\n{sonuc}")

    except Exception as e:
        print(f"{Renk.kirmizi('[Oneshot]')} Komut hatasi: {e}")
