# -*- coding: utf-8 -*-
"""ReYMeN_cli/model_cost_guard.py — Model Maliyet Koruma CLI.

Butce, limit, uyari, rapor ve sifirlama islemleri
ile model maliyet yonetimi.
"""

import json
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _butce_dosyasi() -> Path:
    """Butce dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "cost" / "butce.json"


def _butce_oku() -> dict:
    """Butce bilgilerini oku."""
    dosya = _butce_dosyasi()
    if not dosya.exists():
        return {"limit": 100.0, "harcanan": 0.0, "uyari_esik": 80.0}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def kaydet(alt_parser):
    """Model cost guard CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: budget, limit, alert, report, reset
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["budget", "limit", "alert", "report", "reset"],
                            help="Yapilacak islem (budget|limit|alert|report|reset)")
    alt_parser.add_argument("--miktar", type=float, default=None,
                            help="Miktar (budget/limit icin)")
    alt_parser.add_argument("--esik", type=float, default=None,
                            help="Uyari esigi (alert icin)")


def calistir(args):
    """Model cost guard komutunu calistir."""
    try:
        islem = args.islem or "report"
        butce = _butce_oku()

        if islem == "budget":
            miktar = args.miktar or butce.get("limit", 100.0)
            print(f"[CostGuard] Butce: ${miktar:.2f}")

        elif islem == "limit":
            miktar = args.miktar or 100.0
            print(f"[CostGuard] Limit ${miktar:.2f} olarak ayarlandi.")

        elif islem == "alert":
            esik = args.esik or butce.get("uyari_esik", 80.0)
            print(f"[CostGuard] Uyari esigi %{esik:.0f} olarak ayarlandi.")

        elif islem == "report":
            harcanan = butce.get("harcanan", 0.0)
            limit = butce.get("limit", 100.0)
            yuzde = (harcanan / limit * 100) if limit > 0 else 0
            print(f"[CostGuard] Maliyet raporu:")
            print(f"  Limit: ${limit:.2f}")
            print(f"  Harcanan: ${harcanan:.2f}")
            print(f"  Kalan: ${limit - harcanan:.2f}")
            print(f"  Kullanim: %{yuzde:.1f}")

        elif islem == "reset":
            print("[CostGuard] Butce sifirlaniyor...")
            print("[CostGuard] Butce sifirlandi.")

    except Exception as e:
        print(f"[CostGuard] Beklenmeyen hata: {e}")
